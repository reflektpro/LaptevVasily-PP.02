"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import Product

__version__ = "0.5.0"

__all__ = ["CsvRowError", "Product", "import_products", "__version__"]
