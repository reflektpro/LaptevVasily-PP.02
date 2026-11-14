"""Запись рациона: продукт, масса и приём пищи."""

from dataclasses import dataclass

from calorie_calc.models import PortionNutrients, Product, calculate_portion

MEAL_TYPES = ("завтрак", "обед", "ужин", "перекус")


@dataclass(frozen=True)
class MealEntry:
    """Одна запись рациона.

    Хранит продукт, массу в граммах и приём пищи (завтрак, обед, ужин
    или перекус). Масса должна быть числом больше нуля.
    """

    product: Product
    grams: float
    meal: str

    def __post_init__(self) -> None:
        if not isinstance(self.product, Product):
            raise ValueError("ожидается продукт")

        if not isinstance(self.meal, str):
            raise ValueError("приём пищи должен быть строкой")
        meal = self.meal.strip().lower()
        if meal not in MEAL_TYPES:
            raise ValueError(
                "приём пищи должен быть одним из: " + ", ".join(MEAL_TYPES)
            )
        object.__setattr__(self, "meal", meal)

        # проверка массы выполняется при расчёте порции
        calculate_portion(self.product, self.grams)
        object.__setattr__(self, "grams", float(self.grams))

    def nutrients(self) -> PortionNutrients:
        """КБЖУ этой записи."""
        return calculate_portion(self.product, self.grams)
