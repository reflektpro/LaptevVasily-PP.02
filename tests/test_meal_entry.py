"""Проверка записи рациона."""

import pytest

from calorie_calc import MealEntry, PortionNutrients, Product


def _milk() -> Product:
    return Product(
        id=2,
        name="Молоко 2.5%",
        kcal_per_100g=52,
        protein_per_100g=2.8,
        fat_per_100g=2.5,
        carbs_per_100g=4.7,
    )


def test_entry_keeps_fields():
    entry = MealEntry(_milk(), 200, "завтрак")
    assert entry.product.name == "Молоко 2.5%"
    assert entry.grams == 200.0
    assert entry.meal == "завтрак"


def test_meal_is_normalized():
    assert MealEntry(_milk(), 100, "  Обед ").meal == "обед"


def test_nutrients():
    assert MealEntry(_milk(), 250, "перекус").nutrients() == PortionNutrients(
        kcal=130.0, protein=7.0, fat=6.25, carbs=11.75
    )


@pytest.mark.parametrize("meal", ["", "полдник", None, 5])
def test_wrong_meal(meal):
    with pytest.raises(ValueError):
        MealEntry(_milk(), 100, meal)


@pytest.mark.parametrize("grams", [0, -5, float("nan"), True, "100"])
def test_wrong_grams(grams):
    with pytest.raises(ValueError):
        MealEntry(_milk(), grams, "ужин")


def test_wrong_product():
    with pytest.raises(ValueError):
        MealEntry("молоко", 100, "ужин")
