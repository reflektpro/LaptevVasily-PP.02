"""Тесты загрузки продуктов из CSV или JSON по расширению (день 19)."""

import json
from pathlib import Path

import pytest

from calorie_calc import (
    SUPPORTED_EXTENSIONS,
    CsvRowError,
    JsonItemError,
    ProductCatalog,
    import_products,
    load_products,
)
from calorie_calc.cli import run

DATA = Path(__file__).resolve().parents[1] / "data"


def _json(tmp_path: Path, name: str = "products.json") -> Path:
    path = tmp_path / name
    path.write_text(
        json.dumps(
            [
                {"name": "Яблоко", "kcal": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                {"name": "", "kcal": 1, "protein": 1, "fat": 1, "carbs": 1},
                {"name": "Хлеб", "kcal": 250, "protein": 8, "fat": 3, "carbs": 50},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def test_supported_extensions():
    assert SUPPORTED_EXTENSIONS == (".csv", ".json")


def test_csv_and_json_from_data_are_equal():
    from_csv = load_products(DATA / "products.csv")
    from_json = load_products(DATA / "products.json")
    assert len(from_csv) == 26
    assert from_csv == from_json == import_products(DATA / "products.csv")


def test_json_errors_are_collected(tmp_path):
    errors: list = []
    products = load_products(_json(tmp_path), errors)
    assert [p.name for p in products] == ["Яблоко", "Хлеб"]
    assert len(errors) == 1
    assert isinstance(errors[0], JsonItemError)
    assert errors[0].item == 2


def test_csv_errors_are_collected(tmp_path):
    path = tmp_path / "p.csv"
    path.write_text("name,kcal,protein,fat,carbs\n,1,1,1,1\n", encoding="utf-8")
    errors: list = []
    assert load_products(path, errors) == []
    assert len(errors) == 1 and isinstance(errors[0], CsvRowError)


def test_extension_case_insensitive(tmp_path):
    path = _json(tmp_path, "PRODUCTS.JSON")
    assert len(load_products(path)) == 2


def test_str_path_accepted(tmp_path):
    assert len(load_products(str(_json(tmp_path)))) == 2


@pytest.mark.parametrize("name", ["products.txt", "products", "products.xlsx"])
def test_unsupported_extension(tmp_path, name):
    # Файла нет: при неверном расширении он даже не открывается.
    with pytest.raises(ValueError, match="неподдерживаемый формат"):
        load_products(tmp_path / name)


def test_catalog_loads_json(tmp_path):
    errors: list = []
    catalog = ProductCatalog(_json(tmp_path), errors)
    assert len(catalog) == 2
    assert [p.id for p in catalog.products] == [1, 2]
    assert catalog.find_by_name("хлеб")[0].kcal_per_100g == 250
    assert errors[0].item == 2


def test_catalog_json_then_add_continues_ids(tmp_path):
    catalog = ProductCatalog(_json(tmp_path))
    added = catalog.add_product("Сыр", 350, 25, 27, 0)
    assert added.id == 3


def _run_menu(monkeypatch, capsys, answers) -> str:
    items = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(items))
    run(ProductCatalog())
    return capsys.readouterr().out


def test_cli_imports_json(monkeypatch, capsys, tmp_path):
    out = _run_menu(monkeypatch, capsys, ["1", str(_json(tmp_path)), "0"])
    assert "Загружено продуктов: 2." in out
    assert "Элемент 2:" in out


def test_cli_rejects_unsupported_extension(monkeypatch, capsys, tmp_path):
    out = _run_menu(monkeypatch, capsys, ["1", str(tmp_path / "base.txt"), "0"])
    assert "Поддерживаются только файлы .csv и .json." in out
