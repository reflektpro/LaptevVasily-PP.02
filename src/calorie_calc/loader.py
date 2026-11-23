"""Загрузка базы продуктов из файла: формат выбирается по расширению."""

from pathlib import Path

from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.json_import import JsonItemError, import_products_json
from calorie_calc.models import Product

SUPPORTED_EXTENSIONS = (".csv", ".json")

def load_products(
    path: str | Path,
    errors: list[CsvRowError | JsonItemError] | None = None,
) -> list[Product]:
    """Прочитать продукты из CSV или JSON в зависимости от расширения файла.

    Расширение сравнивается без учёта регистра: .csv читается через
    import_products, .json — через import_products_json. Ошибки строк
    или элементов дописываются в errors так же, как в этих функциях.
    Для другого расширения или файла без расширения выбрасывается
    ValueError, файл при этом не открывается.
    """
    suffix = Path(path).suffix.casefold()
    if suffix == ".csv":
        return import_products(path, errors)
    if suffix == ".json":
        return import_products_json(path, errors)
    raise ValueError(
        "неподдерживаемый формат файла: ожидается .csv или .json"
    )
