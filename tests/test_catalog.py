"""Проверка каталога: хранение продуктов и загрузка CSV при создании."""

from pathlib import Path

from calorie_calc import CsvRowError, Product, ProductCatalog
from calorie_calc.catalog import ProductCatalog as ProductCatalogImpl

_PRODUCTS_CSV = Path(__file__).resolve().parents[1] / "data" / "products.csv"


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
