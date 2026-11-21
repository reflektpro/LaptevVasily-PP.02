"""Импорт CSV на граничных случаях: кодировка, разделитель, пустой файл."""

from pathlib import Path

import pytest

from calorie_calc import CsvRowError, Product, ProductCatalog, import_products

_HEADER = "name,kcal,protein,fat,carbs\n"


def _write(tmp_path: Path, text: str, encoding: str = "utf-8") -> Path:
    path = tmp_path / "products.csv"
    path.write_text(text, encoding=encoding)
    return path


def test_utf8_bom_is_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, _HEADER + "Яблоко,52,0.3,0.2,14\n", "utf-8-sig")
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert errors == []
    assert products == [Product(1, "Яблоко", 52, 0.3, 0.2, 14)]


def test_non_utf8_file_reports_error(tmp_path: Path) -> None:
    path = _write(tmp_path, _HEADER + "Яблоко,52,0.3,0.2,14\n", "cp1251")
    errors: list[CsvRowError] = []

    assert import_products(path, errors) == []
    assert errors == [CsvRowError(1, "файл должен быть в кодировке UTF-8")]


def test_semicolon_delimiter_with_decimal_comma(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "name;kcal;protein;fat;carbs\n"
        "Овсянка;379;13;6,5;67\n"
        "Молоко 2,5%;52;2,8;2,5;4,7\n",
    )
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert errors == []
    assert products == [
        Product(1, "Овсянка", 379, 13, 6.5, 67),
        Product(2, "Молоко 2,5%", 52, 2.8, 2.5, 4.7),
    ]


def test_semicolon_file_keeps_row_validation(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "name;kcal;protein;fat;carbs\n"
        "Сыр;363;23,2;-1;0\n"
        "Вода;0;0;0;0\n",
    )
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert products == [Product(1, "Вода", 0, 0, 0, 0)]
    assert errors == [CsvRowError(2, "поле fat должно быть ≥ 0")]


@pytest.mark.parametrize("text", ["", "\n", _HEADER])
def test_empty_file_or_header_only_gives_empty_list(
    tmp_path: Path, text: str
) -> None:
    errors: list[CsvRowError] = []

    assert import_products(_write(tmp_path, text), errors) == []
    if text == _HEADER:
        assert errors == []


def test_spaces_around_header_names_are_ignored(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        " name , kcal ,protein, fat ,carbs \n"
        "Банан,89,1.1,0.3,22.8\n",
    )

    assert import_products(path) == [Product(1, "Банан", 89, 1.1, 0.3, 22.8)]


def test_crlf_line_endings_and_quoted_name(tmp_path: Path) -> None:
    path = tmp_path / "products.csv"
    path.write_bytes(
        (
            "name,kcal,protein,fat,carbs\r\n"
            '"Хлеб, ржаной",174,6.6,1.2,33.4\r\n'
            "Пшено,348,11.5,3.3,69.3\r\n"
        ).encode("utf-8")
    )
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert errors == []
    assert [p.name for p in products] == ["Хлеб, ржаной", "Пшено"]
    assert products[1].fat_per_100g == 3.3


def test_ambiguous_number_with_comma_and_dot_is_rejected(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "name;kcal;protein;fat;carbs\nТест;1,000.5;1;1;1\n",
    )
    errors: list[CsvRowError] = []

    assert import_products(path, errors) == []
    assert errors == [CsvRowError(2, "поле kcal должно быть числом")]


def test_catalog_loads_semicolon_csv_with_bom(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "name;kcal;protein;fat;carbs\nКефир 1%;40;3;1;4\n",
        "utf-8-sig",
    )

    catalog = ProductCatalog(path)

    assert [p.name for p in catalog.find_by_name("кефир")] == ["Кефир 1%"]
