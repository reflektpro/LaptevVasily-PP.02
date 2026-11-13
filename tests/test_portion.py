"""Проверка расчёта КБЖУ порции по массе в граммах."""

import math

import pytest

from calorie_calc import PortionNutrients, Product, ProductCatalog, calculate_portion
from calorie_calc.models import (
    PortionNutrients as PortionNutrientsModel,
    calculate_portion as calculate_portion_impl,
)


def _oats() -> Product:
    return Product(
        id=1,
        name="Овсяные хлопья",
        kcal_per_100g=379,
        protein_per_100g=13.0,
        fat_per_100g=6.5,
        carbs_per_100g=67.0,
    )


def test_portion_api_exported_from_package() -> None:
    assert PortionNutrients is PortionNutrientsModel
    assert calculate_portion is calculate_portion_impl


def test_calculate_portion_scales_per_100g_and_rounds() -> None:
    portion = calculate_portion(_oats(), 50)

    assert portion == PortionNutrients(
        kcal=189.5,
        protein=6.5,
        fat=3.25,
        carbs=33.5,
    )


def test_calculate_portion_of_100g_keeps_product_values() -> None:
    product = _oats()

    assert calculate_portion(product, 100) == PortionNutrients(
        kcal=379.0,
        protein=13.0,
        fat=6.5,
        carbs=67.0,
    )
    assert calculate_portion(product, 100.0) == calculate_portion(product, 100)


def test_calculate_portion_rounds_half_up_to_two_decimals() -> None:
    # 6.5 г жира на 100 г и порция 15 г дают 0.975 → 0.98.
    # 6.5 г жира на 100 г и порция 33 г дают 2.145 → 2.15.
    fifteen = calculate_portion(_oats(), 15)
    thirty_three = calculate_portion(_oats(), 33)

    assert fifteen == PortionNutrients(kcal=56.85, protein=1.95, fat=0.98, carbs=10.05)
    assert thirty_three == PortionNutrients(
        kcal=125.07,
        protein=4.29,
        fat=2.15,
        carbs=22.11,
    )
    assert all(
        value == round(value, 2)
        for value in (fifteen.kcal, fifteen.protein, fifteen.fat, fifteen.carbs)
    )


def test_calculate_portion_of_zero_nutrients_stays_zero() -> None:
    water = Product(
        id=2,
        name="Вода",
        kcal_per_100g=0,
        protein_per_100g=0,
        fat_per_100g=0,
        carbs_per_100g=0,
    )

    assert calculate_portion(water, 250) == PortionNutrients(0.0, 0.0, 0.0, 0.0)


@pytest.mark.parametrize("grams", [0, 0.0, -0.01, -15])
def test_calculate_portion_rejects_non_positive_grams(grams: float) -> None:
    with pytest.raises(ValueError, match="грамм"):
        calculate_portion(_oats(), grams)


@pytest.mark.parametrize(
    "grams",
    ["50", None, True, False, math.nan, math.inf, -math.inf],
)
def test_calculate_portion_rejects_non_numeric_grams(grams: object) -> None:
    with pytest.raises(ValueError, match="грамм"):
        calculate_portion(_oats(), grams)  # type: ignore[arg-type]


def test_calculate_portion_rejects_non_product() -> None:
    with pytest.raises(ValueError, match="продукт"):
        calculate_portion("Овсянка", 100)  # type: ignore[arg-type]


def test_catalog_calculate_portion_matches_function_for_loaded_product() -> None:
    catalog = ProductCatalog()
    product = catalog.find_by_name("яблоко")[0]

    assert catalog.calculate_portion(product, 150) == calculate_portion(product, 150)
    assert catalog.calculate_portion(product, 150) == PortionNutrients(
        kcal=78.0,
        protein=0.45,
        fat=0.3,
        carbs=21.0,
    )
    assert len(catalog) == 26


def test_catalog_calculate_portion_uses_added_product(tmp_path) -> None:
    path = tmp_path / "products.csv"
    path.write_text(
        "name,kcal,protein,fat,carbs\nВода,0,0,0,0\n",
        encoding="utf-8",
    )
    catalog = ProductCatalog(path)
    honey = catalog.add_product("Мёд", 304, 0.8, 0, 82.4)

    assert catalog.calculate_portion(honey, 10) == PortionNutrients(
        kcal=30.4,
        protein=0.08,
        fat=0.0,
        carbs=8.24,
    )


def test_catalog_calculate_portion_rejects_unknown_product(tmp_path) -> None:
    path = tmp_path / "products.csv"
    path.write_text(
        "name,kcal,protein,fat,carbs\nВода,0,0,0,0\n",
        encoding="utf-8",
    )
    catalog = ProductCatalog(path)
    foreign = Product(
        id=9,
        name="Мёд",
        kcal_per_100g=304,
        protein_per_100g=0.8,
        fat_per_100g=0,
        carbs_per_100g=82.4,
    )
    removed = catalog.remove_product(1)

    with pytest.raises(ValueError, match="не найден"):
        catalog.calculate_portion(foreign, 10)
    with pytest.raises(ValueError, match="не найден"):
        catalog.calculate_portion(removed, 100)

    assert calculate_portion(removed, 100) == PortionNutrients(0.0, 0.0, 0.0, 0.0)
    assert catalog.products == ()
