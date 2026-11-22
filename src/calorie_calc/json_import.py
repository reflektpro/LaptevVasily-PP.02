"""Импорт продуктов из JSON-файла."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

from calorie_calc.models import Product

_REQUIRED_FIELDS = ("name", "kcal", "protein", "fat", "carbs")
_NUMERIC_FIELDS = ("kcal", "protein", "fat", "carbs")


@dataclass(frozen=True)
class JsonItemError:
    """Ошибка при импорте продуктов из JSON.

    item — номер элемента списка продуктов, начиная с 1.
    Ошибка всего файла (не JSON, не UTF-8, неверная структура)
    имеет номер 0.
    """

    item: int
    message: str


def import_products_json(
    path: str | Path,
    errors: list[JsonItemError] | None = None,
) -> list[Product]:
    """Прочитать UTF-8 JSON и вернуть список продуктов.

    Файл содержит список объектов либо объект с ключом "products",
    значение которого — такой список. Обязательные поля объекта:
    name (непустая строка), kcal, protein, fat, carbs (числа ≥ 0,
    пищевая ценность на 100 г). Лишние поля игнорируются.
    Метка BOM в начале файла пропускается. Пустой файл даёт пустой
    список. Файл не в UTF-8, некорректный JSON или неверная структура
    дают ошибку с номером 0 и пустой список.

    Идентификаторы назначаются принятым элементам по порядку,
    начиная с 1, как в import_products для CSV. Элемент с ошибкой
    пропускается и идентификатор не занимает; если передан список
    errors, в него дописываются сообщения.
    """
    found = [] if errors is None else errors
    products: list[Product] = []

    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        found.append(JsonItemError(0, "файл должен быть в кодировке UTF-8"))
        return products

    if not text.strip():
        return products

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        found.append(
            JsonItemError(0, f"некорректный JSON (строка {exc.lineno})")
        )
        return products

    if isinstance(data, dict):
        data = data.get("products")
    if not isinstance(data, list):
        found.append(
            JsonItemError(
                0,
                "ожидается список продуктов или объект с ключом products",
            )
        )
        return products

    next_id = 1
    for number, item in enumerate(data, start=1):
        values, item_errors = _parse_item(number, item)
        if values is None:
            found.extend(item_errors)
            continue
        products.append(
            Product(
                id=next_id,
                name=str(values["name"]),
                kcal_per_100g=float(values["kcal"]),
                protein_per_100g=float(values["protein"]),
                fat_per_100g=float(values["fat"]),
                carbs_per_100g=float(values["carbs"]),
            )
        )
        next_id += 1

    return products


def _parse_item(
    number: int,
    item: object,
) -> tuple[dict[str, str | float] | None, list[JsonItemError]]:
    if not isinstance(item, dict):
        return None, [JsonItemError(number, "элемент должен быть объектом")]

    parsed: dict[str, str | float] = {}
    item_errors: list[JsonItemError] = []

    for field in _REQUIRED_FIELDS:
        value = item.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            item_errors.append(
                JsonItemError(number, f"не заполнено обязательное поле {field}")
            )
            continue
        if field not in _NUMERIC_FIELDS:
            if not isinstance(value, str):
                item_errors.append(
                    JsonItemError(number, f"поле {field} должно быть строкой")
                )
            else:
                parsed[field] = value.strip()
            continue

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            item_errors.append(
                JsonItemError(number, f"поле {field} должно быть числом")
            )
        elif value < 0:
            item_errors.append(
                JsonItemError(number, f"поле {field} должно быть ≥ 0")
            )
        else:
            parsed[field] = float(value)

    if item_errors:
        return None, item_errors
    return parsed, []
