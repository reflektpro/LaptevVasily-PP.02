"""Проверка модели Product: создание и базовые инварианты."""

import math

import pytest

from calorie_calc import Product
from calorie_calc.models import Product as ProductModel


def test_product_exported_from_package() -> None:
    assert Product is ProductModel


def test_create_product() -> None:
    product = Product(
        id=1,
        name="Овсянка",
        kcal_per_100g=379.0,
        protein_per_100g=13.0,
        fat_per_100g=6.5,
        carbs_per_100g=67.0,
    )

    assert product.id == 1
    assert product.name == "Овсянка"
    assert product.kcal_per_100g == 379.0
    assert product.protein_per_100g == 13.0
    assert product.fat_per_100g == 6.5
    assert product.carbs_per_100g == 67.0


def test_create_product_strips_name_and_accepts_zero() -> None:
    product = Product(
        id=2,
        name="  Вода  ",
        kcal_per_100g=0,
        protein_per_100g=0,
        fat_per_100g=0,
        carbs_per_100g=0,
    )

    assert product.name == "Вода"
    assert product.kcal_per_100g == 0.0
    assert product.protein_per_100g == 0.0
    assert product.fat_per_100g == 0.0
    assert product.carbs_per_100g == 0.0


def test_products_with_same_fields_are_equal() -> None:
    left = Product(
        id=3,
        name="Яблоко",
        kcal_per_100g=52,
        protein_per_100g=0.3,
        fat_per_100g=0.2,
        carbs_per_100g=14,
    )
    right = Product(
        id=3,
        name="Яблоко",
        kcal_per_100g=52.0,
        protein_per_100g=0.3,
        fat_per_100g=0.2,
        carbs_per_100g=14.0,
    )

    assert left == right


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_empty_name_rejected(name: str) -> None:
    with pytest.raises(ValueError, match="Название продукта"):
        Product(
            id=1,
            name=name,
            kcal_per_100g=1,
            protein_per_100g=0,
            fat_per_100g=0,
            carbs_per_100g=0,
        )


def test_non_string_name_rejected() -> None:
    with pytest.raises(ValueError, match="Название продукта"):
        Product(
            id=1,
            name=None,  # type: ignore[arg-type]
            kcal_per_100g=1,
            protein_per_100g=0,
            fat_per_100g=0,
            carbs_per_100g=0,
        )


@pytest.mark.parametrize(
    "field",
    ["kcal_per_100g", "protein_per_100g", "fat_per_100g", "carbs_per_100g"],
)
def test_negative_nutrients_rejected(field: str) -> None:
    payload = {
        "id": 1,
        "name": "Яблоко",
        "kcal_per_100g": 52.0,
        "protein_per_100g": 0.3,
        "fat_per_100g": 0.2,
        "carbs_per_100g": 14.0,
    }
    payload[field] = -0.01

    with pytest.raises(ValueError, match=field):
        Product(**payload)


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf, "10", True])
def test_non_finite_or_non_numeric_kcal_rejected(bad_value: object) -> None:
    with pytest.raises(ValueError, match="kcal_per_100g"):
        Product(
            id=1,
            name="Яблоко",
            kcal_per_100g=bad_value,  # type: ignore[arg-type]
            protein_per_100g=0,
            fat_per_100g=0,
            carbs_per_100g=0,
        )


@pytest.mark.parametrize("bad_id", ["1", 1.5, None, True])
def test_invalid_id_rejected(bad_id: object) -> None:
    with pytest.raises(ValueError, match="id"):
        Product(
            id=bad_id,  # type: ignore[arg-type]
            name="Яблоко",
            kcal_per_100g=52,
            protein_per_100g=0.3,
            fat_per_100g=0.2,
            carbs_per_100g=14,
        )
