"""Каталог продуктов, загружаемый из CSV при создании."""

from pathlib import Path

from calorie_calc.csv_import import CsvRowError, import_products
from calorie_calc.models import Product

# Пакет лежит в src/calorie_calc, файл базы — в data/ у корня репозитория.
_DEFAULT_PRODUCTS_CSV = (
    Path(__file__).resolve().parents[2] / "data" / "products.csv"
)


class ProductCatalog:
    """Хранит продукты в памяти и загружает их из CSV при создании.

    По умолчанию читается data/products.csv. Чтение и проверка строк
    выполняются через import_products: в каталог попадают только строки
    с заполненными обязательными полями и неотрицательными числами.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        errors: list[CsvRowError] | None = None,
    ) -> None:
        source = _DEFAULT_PRODUCTS_CSV if path is None else path
        self._products = tuple(import_products(source, errors))

    @property
    def products(self) -> tuple[Product, ...]:
        """Продукты в порядке загрузки."""
        return self._products

    def __len__(self) -> int:
        return len(self._products)
