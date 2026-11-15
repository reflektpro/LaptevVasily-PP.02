"""Проверка суммы КБЖУ за день."""

import pytest

from calorie_calc import MealEntry, PortionNutrients, Product, total_nutrients


def _product(name: str, kcal: float, p: float, f: float, c: float) -> Product:
    return Product(
        id=1,
        name=name,
        kcal_per_100g=kcal,
        protein_per_100g=p,
        fat_per_100g=f,
        carbs_per_100g=c,
    )


def test_empty_list_gives_zeros():
    assert total_nutrients([]) == PortionNutrients(0, 0, 0, 0)


def test_sum_of_two_entries():
    milk = _product("Молоко", 52, 2.8, 2.5, 4.7)
    bread = _product("Хлеб", 250, 8, 3, 50)
    entries = [
        MealEntry(milk, 200, "завтрак"),
        MealEntry(bread, 100, "обед"),
    ]
    total = total_nutrients(entries)
    assert total.kcal == 354
    assert total.protein == 13.6
    assert total.fat == 8
    assert total.carbs == 59.4


def test_not_entry_raises():
    with pytest.raises(ValueError):
        total_nutrients(["молоко"])
