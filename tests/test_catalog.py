"""Проверка каталога: загрузка CSV и поиск продуктов по названию."""

from pathlib import Path

import pytest

from calorie_calc import CsvRowError, Product, ProductCatalog
from calorie_calc.catalog import ProductCatalog as ProductCatalogImpl

_PRODUCTS_CSV = Path(__file__).resolve().parents[1] / "data" / "products.csv"


def _catalog_from_rows(tmp_path: Path, body: str) -> ProductCatalog:
    path = tmp_path / "products.csv"
    path.write_text("name,kcal,protein,fat,carbs\n" + body, encoding="utf-8")
    return ProductCatalog(path)


def test_product_catalog_exported_from_package() -> None:
    assert ProductCatalog is ProductCatalogImpl


def test_catalog_loads_bundled_products_at_startup() -> None:
    catalog = ProductCatalog()

    assert len(catalog) == 26
    assert catalog.products[0] == Product(
        id=1,
        name="Овсяные хлопья",
        kcal_per_100g=379,
        protein_per_100g=13.0,
        fat_per_100g=6.5,
        carbs_per_100g=67.0,
    )
    assert catalog.products[-1].name == "Сыр российский"
    assert [product.id for product in catalog.products] == list(range(1, 27))
    assert all(isinstance(product, Product) for product in catalog.products)
    assert ProductCatalog(_PRODUCTS_CSV).products == catalog.products


def test_catalog_skips_invalid_rows_via_import(tmp_path: Path) -> None:
    path = tmp_path / "products.csv"
    path.write_text(
        "name,kcal,protein,fat,carbs\n"
        "Овсянка,379,13,6.5,67\n"
        ",10,1,1,1\n"
        "Вода,0,0,0,0\n",
        encoding="utf-8",
    )
    errors: list[CsvRowError] = []

    catalog = ProductCatalog(path, errors)

    assert [product.name for product in catalog.products] == ["Овсянка", "Вода"]
    assert [product.id for product in catalog.products] == [1, 2]
    assert errors == [CsvRowError(3, "не заполнено обязательное поле name")]


def test_find_by_name_exact_match_precedes_substring(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Сыр российский,363,23.2,30,0\n"
        "Молоко,52,2.8,2.5,4.7\n"
        "Сыр,300,20,20,0\n",
    )

    found = catalog.find_by_name("  СЫР  ")

    assert [product.name for product in found] == ["Сыр", "Сыр российский"]
    assert found[0] == catalog.products[2]


def test_find_by_name_substring_is_case_insensitive(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Хлеб пшеничный,235,7.6,0.8,49.2\n"
        "Молоко,52,2.8,2.5,4.7\n"
        "Хлеб ржаной,174,6.6,1.2,33.4\n",
    )

    found = catalog.find_by_name("хЛеБ")

    assert [product.name for product in found] == [
        "Хлеб пшеничный",
        "Хлеб ржаной",
    ]


def test_find_by_name_on_bundled_catalog() -> None:
    catalog = ProductCatalog()

    assert [product.name for product in catalog.find_by_name("яблоко")] == ["Яблоко"]
    assert [product.name for product in catalog.find_by_name("ХЛЕБ")] == [
        "Хлеб ржаной",
        "Хлеб пшеничный",
    ]


def test_find_by_name_returns_empty_without_match(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")

    assert catalog.find_by_name("яблоко") == ()
    assert catalog.find_by_name("") == ()
    assert catalog.find_by_name("   ") == ()


def test_find_by_name_rejects_non_string(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")

    with pytest.raises(ValueError, match="запрос"):
        catalog.find_by_name(None)  # type: ignore[arg-type]
