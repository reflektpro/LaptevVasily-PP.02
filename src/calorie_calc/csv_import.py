"""Импорт продуктов из CSV-файла."""

import csv
import io
import math
from dataclasses import dataclass
from pathlib import Path

from calorie_calc.models import Product

_REQUIRED_FIELDS = ("name", "kcal", "protein", "fat", "carbs")
_NUMERIC_FIELDS = ("kcal", "protein", "fat", "carbs")


@dataclass(frozen=True)
class CsvRowError:
    """Ошибка в строке CSV при импорте продуктов.

    line — номер строки файла. Заголовок считается строкой 1.
    """

    line: int
    message: str


def import_products(
    path: str | Path,
    errors: list[CsvRowError] | None = None,
) -> list[Product]:
    """Прочитать UTF-8 CSV и вернуть список продуктов.

    Ожидаемые столбцы: name, kcal, protein, fat, carbs.
    Метка BOM в начале файла (UTF-8 с BOM, как сохраняет Excel)
    пропускается, пробелы вокруг названий столбцов отбрасываются.
    Разделитель определяется по заголовку: запятая или точка
    с запятой. В числах допускается десятичная запятая («6,5»).
    Пустой файл или файл только с заголовком дают пустой список.
    Файл не в UTF-8 не читается: в errors добавляется ошибка
    строки 1, результат — пустой список.
    Столбца id в файле нет: идентификаторы назначаются принятым
    строкам по порядку, начиная с 1. Строка с пустым обязательным
    полем, нечисловым значением или числом меньше нуля пропускается
    и идентификатор не занимает. Калорийность и БЖУ записываются
    как пищевая ценность на 100 граммов.

    Если передан список errors, в него дописываются ошибки
    пропущенных строк. Повторный вызов с тем же списком
    накапливает сообщения.
    """
    found = [] if errors is None else errors
    products: list[Product] = []

    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        found.append(CsvRowError(1, "файл должен быть в кодировке UTF-8"))
        return products

    first_line = text.splitlines()[0] if text else ""
    reader = csv.DictReader(
        io.StringIO(text, newline=""),
        delimiter=_detect_delimiter(first_line),
    )
    if reader.fieldnames is None:
        return products
    reader.fieldnames = [name.strip() for name in reader.fieldnames]

    missing_columns = [
        field
        for field in _REQUIRED_FIELDS
        if field not in reader.fieldnames
    ]
    if missing_columns:
        found.append(
            CsvRowError(
                1,
                "в заголовке нет обязательных столбцов: "
                + ", ".join(missing_columns),
            )
        )
        return products

    next_id = 1
    for row in reader:
        values, row_errors = _parse_row(reader.line_num, row)
        if values is None:
            found.extend(row_errors)
            continue
        products.append(_to_product(next_id, values))
        next_id += 1

    return products


def _detect_delimiter(header: str) -> str:
    """Выбрать разделитель по строке заголовка: «;» или «,»."""
    if header.count(";") > header.count(","):
        return ";"
    return ","


def _cell(row: dict[str | None, str | list[str] | None], field: str) -> str | None:
    value = row.get(field)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    return text


def _normalize_decimal(text: str) -> str:
    """Заменить одну десятичную запятую на точку: «6,5» → «6.5»."""
    if text.count(",") == 1 and "." not in text:
        return text.replace(",", ".")
    return text


def _parse_number(text: str) -> tuple[float | None, str | None]:
    """Вернуть число либо причину отказа: number или negative."""
    try:
        value = float(_normalize_decimal(text))
    except ValueError:
        return None, "number"
    if not math.isfinite(value):
        return None, "number"
    if value < 0:
        return None, "negative"
    return value, None


def _parse_row(
    line: int,
    row: dict[str | None, str | list[str] | None],
) -> tuple[dict[str, str | float] | None, list[CsvRowError]]:
    parsed: dict[str, str | float] = {}
    row_errors: list[CsvRowError] = []

    for field in _REQUIRED_FIELDS:
        text = _cell(row, field)
        if text is None:
            row_errors.append(
                CsvRowError(line, f"не заполнено обязательное поле {field}")
            )
            continue
        if field not in _NUMERIC_FIELDS:
            parsed[field] = text
            continue

        number, problem = _parse_number(text)
        if problem == "number":
            row_errors.append(
                CsvRowError(line, f"поле {field} должно быть числом")
            )
        elif problem == "negative":
            row_errors.append(
                CsvRowError(line, f"поле {field} должно быть ≥ 0")
            )
        elif number is not None:
            parsed[field] = number

    if row_errors:
        return None, row_errors
    return parsed, []


def _to_product(product_id: int, values: dict[str, str | float]) -> Product:
    return Product(
        id=product_id,
        name=str(values["name"]),
        kcal_per_100g=float(values["kcal"]),
        protein_per_100g=float(values["protein"]),
        fat_per_100g=float(values["fat"]),
        carbs_per_100g=float(values["carbs"]),
    )
