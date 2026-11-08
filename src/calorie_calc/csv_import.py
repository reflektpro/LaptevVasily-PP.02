"""Импорт продуктов из CSV-файла."""

import csv
from pathlib import Path

from calorie_calc.models import Product


def import_products(path: str | Path) -> list[Product]:
    """Прочитать UTF-8 CSV и вернуть список продуктов.

    Ожидаемые столбцы: name, kcal, protein, fat, carbs.
    Столбца id в файле нет: идентификаторы назначаются по порядку
    строк данных, начиная с 1. Значения kcal, protein, fat и carbs
    записываются как пищевая ценность на 100 граммов.
    """
    products: list[Product] = []
    with Path(path).open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for product_id, row in enumerate(reader, start=1):
            products.append(
                Product(
                    id=product_id,
                    name=row["name"],
                    kcal_per_100g=float(row["kcal"]),
                    protein_per_100g=float(row["protein"]),
                    fat_per_100g=float(row["fat"]),
                    carbs_per_100g=float(row["carbs"]),
                )
            )
    return products
