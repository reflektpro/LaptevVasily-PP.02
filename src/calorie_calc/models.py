"""Модель продукта и расчёт КБЖУ порции."""

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

_NUTRIENT_FIELDS = (
    "kcal_per_100g",
    "protein_per_100g",
    "fat_per_100g",
    "carbs_per_100g",
)


def _non_negative_number(field: str, value: object) -> float:
    """Вернуть число как float, если оно конечное и неотрицательное."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} должно быть неотрицательным числом")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} должно быть неотрицательным числом")
    return float(value)


@dataclass(frozen=True)
class Product:
    """Продукт и его пищевая ценность на 100 граммов.

    Инварианты: название непустое; калорийность и БЖУ не меньше нуля.
    """

    id: int
    name: str
    kcal_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int):
            raise ValueError("id должен быть целым числом")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Название продукта не должно быть пустым")

        object.__setattr__(self, "name", self.name.strip())
        for field in _NUTRIENT_FIELDS:
            object.__setattr__(
                self,
                field,
                _non_negative_number(field, getattr(self, field)),
            )


@dataclass(frozen=True)
class PortionNutrients:
    """Калорийность и БЖУ одной порции.

    Значения уже масштабированы на массу порции и округлены до двух знаков.
    """

    kcal: float
    protein: float
    fat: float
    carbs: float


def calculate_portion(product: Product, grams: float) -> PortionNutrients:
    """Посчитать калорийность и БЖУ порции.

    Пищевая ценность продукта задана на 100 г и масштабируется на массу
    порции. Каждое значение округляется до двух знаков после запятой,
    половина округляется вверх. Масса должна быть числом больше нуля.
    """
    if not isinstance(product, Product):
        raise ValueError("ожидается продукт")

    mass = _positive_grams(grams)
    return PortionNutrients(
        kcal=_scale(product.kcal_per_100g, mass),
        protein=_scale(product.protein_per_100g, mass),
        fat=_scale(product.fat_per_100g, mass),
        carbs=_scale(product.carbs_per_100g, mass),
    )


def _positive_grams(grams: object) -> float:
    """Вернуть массу в граммах, если она — конечное число больше нуля."""
    if isinstance(grams, bool) or not isinstance(grams, (int, float)):
        raise ValueError("граммы должны быть числом больше нуля")
    if not math.isfinite(grams) or grams <= 0:
        raise ValueError("граммы должны быть числом больше нуля")
    return float(grams)


def _scale(per_100g: float, grams: float) -> float:
    """Пересчитать величину с 100 г на массу порции и округлить до 0.01."""
    amount = Decimal(str(per_100g)) * Decimal(str(grams)) / Decimal(100)
    return float(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
