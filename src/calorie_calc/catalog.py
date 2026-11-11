"""Каталог продуктов: загрузка из CSV и поиск по названию."""

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
    Поиск по названию не учитывает регистр: точное совпадение и подстрока.
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

    def find_by_name(self, query: str) -> tuple[Product, ...]:
        """Найти продукты по названию без учёта регистра.

        Сначала идут точные совпадения названия, затем продукты, в названии
        которых запрос встречается как подстрока. Внутри каждой группы
        сохраняется порядок загрузки. Пробелы по краям запроса не учитываются.
        Пустой запрос ничего не находит.
        """
        if not isinstance(query, str):
            raise ValueError("запрос должен быть строкой")

        needle = query.strip().casefold()
        if not needle:
            return ()

        exact: list[Product] = []
        partial: list[Product] = []
        for product in self._products:
            name = product.name.casefold()
            if name == needle:
                exact.append(product)
            elif needle in name:
                partial.append(product)
        return tuple(exact + partial)

    def __len__(self) -> int:
        return len(self._products)
