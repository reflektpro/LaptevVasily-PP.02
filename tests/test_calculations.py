"""Сводные unit-тесты моделей и расчётов."""

import dataclasses
import math

import pytest

from calorie_calc import (
    MealEntry,
    PortionNutrients,
    Product,
    calculate_portion,
    compare_with_norm,
    daily_norm,
    total_nutrients,
)


def _buckwheat() -> Product:
    return Product(
        id=1,
        name="Гречка",
        kcal_per_100g=343,
        protein_per_100g=12.6,
        fat_per_100g=3.3,
        carbs_per_100g=62.1,
    )


def _milk() -> Product:
    return Product(
        id=2,
        name="Молоко 2,5%",
        kcal_per_100g=52,
        protein_per_100g=2.8,
        fat_per_100g=2.5,
        carbs_per_100g=4.7,
    )


def test_models_are_immutable() -> None:
    product = _buckwheat()
    portion = calculate_portion(product, 100)
    entry = MealEntry(product, 100, "обед")

    with pytest.raises(dataclasses.FrozenInstanceError):
        product.name = "Рис"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        portion.kcal = 0  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.grams = 1  # type: ignore[misc]


def test_product_name_is_stripped_and_numbers_become_float() -> None:
    product = Product(1, "  Гречка ", 343, 12, 3, 62)

    assert product.name == "Гречка"
    assert isinstance(product.kcal_per_100g, float)
    assert isinstance(product.protein_per_100g, float)


@pytest.mark.parametrize("grams", [1, 25, 100, 150, 333])
def test_portion_matches_per_100g_proportion(grams: int) -> None:
    product = _buckwheat()
    portion = calculate_portion(product, grams)
    # округление до 0.01 даёт отклонение не больше половины сотой

    assert portion.kcal == pytest.approx(product.kcal_per_100g * grams / 100, abs=0.0051)
    assert portion.protein == pytest.approx(
        product.protein_per_100g * grams / 100, abs=0.0051
    )
    assert portion.fat == pytest.approx(product.fat_per_100g * grams / 100, abs=0.0051)
    assert portion.carbs == pytest.approx(
        product.carbs_per_100g * grams / 100, abs=0.0051
    )


def test_double_mass_gives_double_portion() -> None:
    product = _milk()
    single = calculate_portion(product, 200)
    double = calculate_portion(product, 400)

    assert double.kcal == pytest.approx(single.kcal * 2)
    assert double.protein == pytest.approx(single.protein * 2)
    assert double.fat == pytest.approx(single.fat * 2)
    assert double.carbs == pytest.approx(single.carbs * 2)


def test_day_total_equals_sum_of_portions() -> None:
    entries = [
        MealEntry(_buckwheat(), 80, "завтрак"),
        MealEntry(_milk(), 200, "завтрак"),
        MealEntry(_buckwheat(), 150, "ужин"),
    ]
    total = total_nutrients(entries)
    portions = [entry.nutrients() for entry in entries]

    assert total == PortionNutrients(
        kcal=round(sum(p.kcal for p in portions), 2),
        protein=round(sum(p.protein for p in portions), 2),
        fat=round(sum(p.fat for p in portions), 2),
        carbs=round(sum(p.carbs for p in portions), 2),
    )
    # 274.4 + 104 + 514.5
    assert total.kcal == 892.9


def test_entry_order_does_not_change_total() -> None:
    entries = [
        MealEntry(_buckwheat(), 80, "завтрак"),
        MealEntry(_milk(), 200, "перекус"),
    ]

    assert total_nutrients(entries) == total_nutrients(list(reversed(entries)))


def test_day_compared_with_norm() -> None:
    # 10*60 + 6.25*165 - 5*25 - 161 = 1345.25; * 1.2 = 1614.3
    norm = daily_norm("ж", 60, 165, 25, "минимальная")
    total = total_nutrients(
        [
            MealEntry(_buckwheat(), 80, "завтрак"),
            MealEntry(_milk(), 200, "завтрак"),
            MealEntry(_buckwheat(), 150, "ужин"),
        ]
    )
    result = compare_with_norm(total.kcal, norm)

    assert result == {"remaining": 721.4, "excess": 0.0, "status": "остаток"}
    assert result["remaining"] + total.kcal == pytest.approx(norm)


def test_heavier_person_has_higher_norm() -> None:
    light = daily_norm("м", 60, 175, 30, "средняя")
    heavy = daily_norm("м", 90, 175, 30, "средняя")

    # каждый килограмм добавляет 10 ккал до умножения на коэффициент
    assert heavy - light == pytest.approx(30 * 10 * 1.55)


def test_higher_activity_gives_higher_norm() -> None:
    low = daily_norm("ж", 55, 160, 40, "низкая")
    high = daily_norm("ж", 55, 160, 40, "высокая")

    assert high > low


@pytest.mark.parametrize("bad", [math.inf, -math.inf, math.nan])
@pytest.mark.parametrize("position", [1, 2, 3])
def test_daily_norm_rejects_non_finite(bad: float, position: int) -> None:
    args = ["м", 70, 175, 30, "средняя"]
    args[position] = bad

    with pytest.raises(ValueError):
        daily_norm(*args)


@pytest.mark.parametrize(
    "eaten, norm",
    [(math.inf, 2000), (math.nan, 2000), (1500, math.inf), (1500, math.nan)],
)
def test_compare_with_norm_rejects_non_finite(eaten: float, norm: float) -> None:
    with pytest.raises(ValueError):
        compare_with_norm(eaten, norm)
