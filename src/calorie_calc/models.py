"""Модель продукта для калькулятора калорий."""

import math
from dataclasses import dataclass

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
