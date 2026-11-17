"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.diary import MEAL_TYPES, MealEntry, total_nutrients
from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import PortionNutrients, Product, calculate_portion
from calorie_calc.norm import ACTIVITY_LEVELS, daily_norm

__version__ = "0.13.0"

__all__ = [
    "ACTIVITY_LEVELS",
    "MEAL_TYPES",
    "MealEntry",
    "CsvRowError",
    "PortionNutrients",
    "Product",
    "ProductCatalog",
    "calculate_portion",
    "daily_norm",
    "import_products",
    "total_nutrients",
    "__version__",
]
