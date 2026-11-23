"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.diary import MEAL_TYPES, MealEntry, total_nutrients
from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.json_import import JsonItemError, import_products_json
from calorie_calc.loader import SUPPORTED_EXTENSIONS, load_products
from calorie_calc.models import PortionNutrients, Product, calculate_portion
from calorie_calc.report import export_report_csv, export_report_text
from calorie_calc.norm import ACTIVITY_LEVELS, compare_with_norm, daily_norm

__version__ = "0.19.0"

__all__ = [
    "ACTIVITY_LEVELS",
    "MEAL_TYPES",
    "SUPPORTED_EXTENSIONS",
    "MealEntry",
    "CsvRowError",
    "JsonItemError",
    "PortionNutrients",
    "Product",
    "ProductCatalog",
    "calculate_portion",
    "compare_with_norm",
    "daily_norm",
    "export_report_csv",
    "export_report_text",
    "import_products",
    "import_products_json",
    "load_products",
    "total_nutrients",
    "__version__",
]
