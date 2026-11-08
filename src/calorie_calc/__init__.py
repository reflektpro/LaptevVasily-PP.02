"""Модуль калькулятора калорий. Учебная практика ПП.02."""

from calorie_calc.csv_import import import_products
from calorie_calc.models import Product

__version__ = "0.4.0"

__all__ = ["Product", "import_products", "__version__"]
