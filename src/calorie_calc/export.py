"""Экспорт базы продуктов в CSV или JSON — в тех же форматах, что читает импорт."""

import csv
import json
from pathlib import Path

from calorie_calc.models import Product

# Те же столбцы и ключи, что ожидают import_products и import_products_json.
EXPORT_FIELDS = ("name", "kcal", "protein", "fat", "carbs")


def _number(value: float) -> int | float:
    """Целое значение записываем без «.0», как в data/products.csv."""
    return int(value) if float(value).is_integer() else value


def _rows(products) -> list[dict[str, object]]:
    products = list(products)
    rows = []
    for product in products:
        if not isinstance(product, Product):
            raise ValueError("ожидается продукт")
        rows.append(
            {
                "name": product.name,
                "kcal": _number(product.kcal_per_100g),
                "protein": _number(product.protein_per_100g),
                "fat": _number(product.fat_per_100g),
                "carbs": _number(product.carbs_per_100g),
            }
        )
    return rows


def export_products_csv(products, path: str | Path) -> Path:
    """Сохранить продукты в CSV (UTF-8, разделитель «,», точка в числах).

    Столбцы name, kcal, protein, fat, carbs — файл снова читается
    через import_products. Идентификаторы не сохраняются: при импорте
    они назначаются заново по порядку строк.
    """
    rows = _rows(products)
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_products_json(products, path: str | Path) -> Path:
    """Сохранить продукты в JSON: объект с ключом products (UTF-8, отступ 2).

    Формат совпадает с data/products.json и читается через
    import_products_json. Кириллица записывается как есть.
    """
    rows = _rows(products)
    path = Path(path)
    path.write_text(
        json.dumps({"products": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def save_products(products, path: str | Path) -> Path:
    """Сохранить продукты в CSV или JSON в зависимости от расширения файла.

    Расширение сравнивается без учёта регистра. Для другого расширения
    или файла без расширения выбрасывается ValueError, файл не создаётся.
    """
    suffix = Path(path).suffix.casefold()
    if suffix == ".csv":
        return export_products_csv(products, path)
    if suffix == ".json":
        return export_products_json(products, path)
    raise ValueError(
        "неподдерживаемый формат файла: ожидается .csv или .json"
    )
