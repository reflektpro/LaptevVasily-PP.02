"""Проверка строк CSV при импорте продуктов."""

from pathlib import Path

import pytest

from calorie_calc import CsvRowError, Product, import_products

_PRODUCTS_CSV = Path(__file__).resolve().parents[1] / "data" / "products.csv"
_HEADER = "name,kcal,protein,fat,carbs\n"


def _csv(tmp_path: Path, body: str, header: str = _HEADER) -> Path:
    path = tmp_path / "products.csv"
    path.write_text(header + body, encoding="utf-8")
    return path


def test_invalid_rows_are_skipped_and_errors_accumulated(tmp_path: Path) -> None:
    path = _csv(
        tmp_path,
        "Овсянка,379,13,6.5,67\n"
        "   ,10,1,1,1\n"
        "Яблоко,нет,0.3,0.2,14\n"
        "Сыр,363,23.2,-1,0\n"
        "Вода,0,0,0,0\n",
    )
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert products == [
        Product(
            id=1,
            name="Овсянка",
            kcal_per_100g=379,
            protein_per_100g=13,
            fat_per_100g=6.5,
            carbs_per_100g=67,
        ),
        Product(
            id=2,
            name="Вода",
            kcal_per_100g=0,
            protein_per_100g=0,
            fat_per_100g=0,
            carbs_per_100g=0,
        ),
    ]
    assert errors == [
        CsvRowError(3, "не заполнено обязательное поле name"),
        CsvRowError(4, "поле kcal должно быть числом"),
        CsvRowError(5, "поле fat должно быть ≥ 0"),
    ]


def test_one_row_accumulates_each_field_error(tmp_path: Path) -> None:
    path = _csv(tmp_path, "Плохо,,abc,-2,\n")
    errors: list[CsvRowError] = []

    products = import_products(path, errors)

    assert products == []
    assert errors == [
        CsvRowError(2, "не заполнено обязательное поле kcal"),
        CsvRowError(2, "поле protein должно быть числом"),
        CsvRowError(2, "поле fat должно быть ≥ 0"),
        CsvRowError(2, "не заполнено обязательное поле carbs"),
    ]


@pytest.mark.parametrize("raw", ["нет", "nan", "inf"])
def test_non_finite_or_non_numeric_value_is_rejected(
    tmp_path: Path, raw: str
) -> None:
    path = _csv(tmp_path, f"Яблоко,{raw},0.3,0.2,14\n")
    errors: list[CsvRowError] = []

    assert import_products(path, errors) == []
    assert errors == [CsvRowError(2, "поле kcal должно быть числом")]


def test_missing_required_columns_reported_once(tmp_path: Path) -> None:
    path = _csv(tmp_path, "Хлеб,200,8,1\n", header="name,kcal,protein,fat\n")
    errors: list[CsvRowError] = []

    assert import_products(path, errors) == []
    assert errors == [
        CsvRowError(1, "в заголовке нет обязательных столбцов: carbs")
    ]


def test_errors_append_to_existing_list(tmp_path: Path) -> None:
    path = _csv(tmp_path, ",1,1,1,1\n")
    errors = [CsvRowError(9, "раньше")]

    assert import_products(path, errors) == []
    assert errors == [
        CsvRowError(9, "раньше"),
        CsvRowError(2, "не заполнено обязательное поле name"),
    ]


def test_invalid_rows_skipped_without_error_list(tmp_path: Path) -> None:
    path = _csv(tmp_path, "Плохо,-1,1,1,1\nВода,0,0,0,0\n")

    products = import_products(path)

    assert [product.name for product in products] == ["Вода"]
    assert products[0].id == 1


def test_bundled_products_csv_has_no_row_errors() -> None:
    errors: list[CsvRowError] = []

    products = import_products(_PRODUCTS_CSV, errors)

    assert errors == []
    assert len(products) == 26
