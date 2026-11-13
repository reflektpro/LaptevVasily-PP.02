"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import PortionNutrients, Product, calculate_portion

__version__ = "0.9.0"

__all__ = [
    "CsvRowError",
    "PortionNutrients",
    "Product",
    "ProductCatalog",
    "calculate_portion",
    "import_products",
    "__version__",
]
