"""Проверка каталога: загрузка CSV, поиск и изменение списка продуктов."""

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


def test_add_product_appends_with_next_id_and_is_searchable(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")

    added = catalog.add_product("  Мёд  ", 304, 0.3, 0, 82.4)

    assert added == Product(
        id=2,
        name="Мёд",
        kcal_per_100g=304,
        protein_per_100g=0.3,
        fat_per_100g=0,
        carbs_per_100g=82.4,
    )
    assert catalog.products == (catalog.products[0], added)
    assert catalog.find_by_name("мёд") == (added,)
    assert len(catalog) == 2


def test_add_product_to_empty_catalog_starts_at_one(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "")

    added = catalog.add_product("Вода", 0, 0, 0, 0)

    assert added.id == 1
    assert catalog.products == (added,)


def test_add_product_rejects_duplicate_name_ignoring_case(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Яблоко,52,0.3,0.2,14\n")
    before = catalog.products

    with pytest.raises(ValueError, match="названием"):
        catalog.add_product("  яБлОкО ", 50, 0, 0, 0)

    assert catalog.products == before

    added = catalog.add_product("Груша", 57, 0.4, 0.1, 15.2)
    assert added.id == 2


def test_add_product_rejects_invalid_values(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")

    with pytest.raises(ValueError, match="Название продукта"):
        catalog.add_product("   ", 0, 0, 0, 0)
    with pytest.raises(ValueError, match="kcal_per_100g"):
        catalog.add_product("Мёд", -1, 0, 0, 0)

    assert [product.name for product in catalog.products] == ["Вода"]


def test_search_order_includes_added_product(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Сыр российский,363,23.2,30,0\n")
    catalog.add_product("Сыр", 300, 20, 20, 0)

    found = catalog.find_by_name("сыр")

    assert [product.name for product in found] == ["Сыр", "Сыр российский"]


def test_update_product_replaces_fields_and_keeps_place(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Молоко,52,2.8,2.5,4.7\n"
        "Вода,0,0,0,0\n",
    )

    same_name = catalog.update_product(1, "  МОЛОКО ", 60, 3, 3, 5)
    renamed = catalog.update_product(1, "молоко 2.5%", 52, 2.8, 2.5, 4.7)

    assert same_name.name == "МОЛОКО"
    assert renamed == Product(
        id=1,
        name="молоко 2.5%",
        kcal_per_100g=52,
        protein_per_100g=2.8,
        fat_per_100g=2.5,
        carbs_per_100g=4.7,
    )
    assert catalog.products == (renamed, catalog.products[1])
    assert catalog.products[1].name == "Вода"
    assert catalog.find_by_name("МОЛОКО") == (renamed,)


def test_update_product_rejects_duplicate_name_of_another_product(
    tmp_path: Path,
) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Молоко,52,2.8,2.5,4.7\n"
        "Вода,0,0,0,0\n",
    )
    before = catalog.products

    with pytest.raises(ValueError, match="названием"):
        catalog.update_product(1, "  ВОДА ", 1, 0, 0, 0)

    assert catalog.products == before


def test_update_product_rejects_missing_and_invalid(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")
    before = catalog.products

    with pytest.raises(ValueError, match="не найден"):
        catalog.update_product(9, "Сок", 40, 0, 0, 10)
    with pytest.raises(ValueError, match="protein_per_100g"):
        catalog.update_product(1, "Вода", 0, -1, 0, 0)
    with pytest.raises(ValueError, match="id"):
        catalog.update_product(True, "Вода", 0, 0, 0, 0)  # type: ignore[arg-type]

    assert catalog.products == before


def test_remove_product_drops_it_from_search(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Молоко,52,2.8,2.5,4.7\n"
        "Вода,0,0,0,0\n"
        "Сок,40,0.1,0,10\n",
    )

    removed = catalog.remove_product(2)

    assert removed.name == "Вода"
    assert [product.name for product in catalog.products] == ["Молоко", "Сок"]
    assert [product.id for product in catalog.products] == [1, 3]
    assert catalog.find_by_name("вода") == ()
    assert [product.name for product in catalog.find_by_name("о")] == [
        "Молоко",
        "Сок",
    ]


def test_remove_product_rejects_missing_id(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(tmp_path, "Вода,0,0,0,0\n")
    before = catalog.products

    with pytest.raises(ValueError, match="не найден"):
        catalog.remove_product(5)
    with pytest.raises(ValueError, match="id"):
        catalog.remove_product("1")  # type: ignore[arg-type]

    assert catalog.products == before


def test_add_after_remove_does_not_reuse_id(tmp_path: Path) -> None:
    catalog = _catalog_from_rows(
        tmp_path,
        "Вода,0,0,0,0\nЯблоко,52,0.3,0.2,14\n",
    )

    catalog.remove_product(2)
    added = catalog.add_product("Груша", 57, 0.4, 0.1, 15.2)

    assert added.id == 3
    assert [product.id for product in catalog.products] == [1, 3]
    assert catalog.find_by_name("яблоко") == ()
