"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.diary import MEAL_TYPES, MealEntry
from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import PortionNutrients, Product, calculate_portion

__version__ = "0.10.0"

__all__ = [
    "MEAL_TYPES",
    "MealEntry",
    "CsvRowError",
    "PortionNutrients",
    "Product",
    "ProductCatalog",
    "calculate_portion",
    "import_products",
    "__version__",
]
