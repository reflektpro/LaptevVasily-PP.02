"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import Product

__version__ = "0.8.0"

__all__ = [
    "CsvRowError",
    "Product",
    "ProductCatalog",
    "import_products",
    "__version__",
]
