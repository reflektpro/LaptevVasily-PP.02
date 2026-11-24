"""Тесты экспорта каталога продуктов в CSV и JSON (день 20)."""

import csv
import json
from pathlib import Path

import pytest

from calorie_calc import (
    EXPORT_FIELDS,
    Product,
    ProductCatalog,
    export_products_csv,
    export_products_json,
    import_products,
    import_products_json,
    load_products,
    save_products,
)

DATA = Path(__file__).resolve().parents[1] / "data"


def _products() -> list[Product]:
    return [
        Product(1, "Яблоко", 52, 0.3, 0.2, 14),
        Product(2, 'Хлеб "Бородинский", ржаной', 208, 6.8, 1.3, 40.7),
    ]


def _values(products):
    return [
        (p.name, p.kcal_per_100g, p.protein_per_100g, p.fat_per_100g, p.carbs_per_100g)
        for p in products
    ]


def test_export_fields_match_import_columns():
    assert EXPORT_FIELDS == ("name", "kcal", "protein", "fat", "carbs")


def test_csv_header_and_integer_format(tmp_path):
    path = export_products_csv(_products(), tmp_path / "out.csv")
    assert path == tmp_path / "out.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "name,kcal,protein,fat,carbs"
    assert lines[1] == "Яблоко,52,0.3,0.2,14"


def test_csv_round_trip_with_quotes_and_comma(tmp_path):
    path = export_products_csv(_products(), tmp_path / "out.csv")
    errors = []
    loaded = import_products(path, errors)
    assert errors == []
    assert _values(loaded) == _values(_products())
    assert [p.id for p in loaded] == [1, 2]


def test_json_structure_and_cyrillic(tmp_path):
    path = export_products_json(_products(), tmp_path / "out.json")
    text = path.read_text(encoding="utf-8")
    assert "Яблоко" in text
    data = json.loads(text)
    assert list(data) == ["products"]
    assert data["products"][0] == {
        "name": "Яблоко", "kcal": 52, "protein": 0.3, "fat": 0.2, "carbs": 14,
    }


def test_json_round_trip(tmp_path):
    path = export_products_json(_products(), tmp_path / "out.json")
    errors = []
    assert _values(import_products_json(path, errors)) == _values(_products())
    assert errors == []


def test_empty_list_exports_and_imports_empty(tmp_path):
    csv_path = export_products_csv([], tmp_path / "empty.csv")
    json_path = export_products_json([], tmp_path / "empty.json")
    assert csv_path.read_text(encoding="utf-8").strip() == "name,kcal,protein,fat,carbs"
    assert json.loads(json_path.read_text(encoding="utf-8")) == {"products": []}
    assert import_products(csv_path) == []
    assert import_products_json(json_path) == []


@pytest.mark.parametrize("func", [export_products_csv, export_products_json])
def test_non_product_rejected_and_file_not_created(tmp_path, func):
    path = tmp_path / "bad.out"
    with pytest.raises(ValueError):
        func([_products()[0], "не продукт"], path)
    assert not path.exists()


@pytest.mark.parametrize("name", ["a.csv", "B.CSV", "c.json", "D.Json"])
def test_save_products_by_extension_round_trip(tmp_path, name):
    path = save_products(_products(), tmp_path / name)
    assert _values(load_products(path)) == _values(_products())


@pytest.mark.parametrize("name", ["a.txt", "noext", "a.xlsx"])
def test_save_products_unsupported_extension(tmp_path, name):
    with pytest.raises(ValueError):
        save_products(_products(), tmp_path / name)
    assert not (tmp_path / name).exists()


def test_data_csv_converts_to_same_json(tmp_path):
    products = import_products(DATA / "products.csv")
    path = export_products_json(products, tmp_path / "products.json")
    assert _values(import_products_json(path)) == _values(
        import_products_json(DATA / "products.json")
    )


def test_catalog_save_keeps_changes(tmp_path):
    catalog = ProductCatalog(DATA / "products.csv")
    catalog.add_product("Киви", 47, 0.8, 0.4, 8.1)
    first = catalog.products[0]
    catalog.remove_product(first.id)
    for name in ("catalog.csv", "catalog.json"):
        path = catalog.save(tmp_path / name)
        reloaded = ProductCatalog(path)
        assert len(reloaded) == len(catalog)
        assert _values(reloaded.products) == _values(catalog.products)
        assert reloaded.find_by_name("киви")


def test_catalog_save_unsupported_extension(tmp_path):
    catalog = ProductCatalog(DATA / "products.csv")
    with pytest.raises(ValueError):
        catalog.save(tmp_path / "catalog.txt")
