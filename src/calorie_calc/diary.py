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


def total_nutrients(entries) -> PortionNutrients:
    """Сумма КБЖУ по списку записей рациона за день.

    Для пустого списка возвращает нули. Итог округляется до двух знаков.
    """
    kcal = protein = fat = carbs = 0.0
    for entry in entries:
        if not isinstance(entry, MealEntry):
            raise ValueError("ожидается запись рациона")
        item = entry.nutrients()
        kcal += item.kcal
        protein += item.protein
        fat += item.fat
        carbs += item.carbs
    return PortionNutrients(
        kcal=round(kcal, 2),
        protein=round(protein, 2),
        fat=round(fat, 2),
        carbs=round(carbs, 2),
    )
