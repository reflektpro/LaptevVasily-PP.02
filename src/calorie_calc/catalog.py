"""Каталог продуктов: загрузка из CSV, поиск и изменение списка."""

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
    Продукт можно добавить, обновить и удалить. Название в каталоге
    уникально без учёта регистра.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        errors: list[CsvRowError] | None = None,
    ) -> None:
        source = _DEFAULT_PRODUCTS_CSV if path is None else path
        self._products = list(import_products(source, errors))
        self._next_id = (
            max((product.id for product in self._products), default=0) + 1
        )

    @property
    def products(self) -> tuple[Product, ...]:
        """Продукты в порядке загрузки и последующего добавления."""
        return tuple(self._products)

    def add_product(
        self,
        name: str,
        kcal_per_100g: float,
        protein_per_100g: float,
        fat_per_100g: float,
        carbs_per_100g: float,
    ) -> Product:
        """Добавить продукт в конец каталога и вернуть его.

        Идентификатор назначает каталог: следующий после уже выданных,
        в том числе удалённых. Название и пищевая ценность проверяются
        так же, как при создании Product. Если такое название уже есть
        без учёта регистра, продукт не добавляется.
        """
        product = Product(
            id=self._next_id,
            name=name,
            kcal_per_100g=kcal_per_100g,
            protein_per_100g=protein_per_100g,
            fat_per_100g=fat_per_100g,
            carbs_per_100g=carbs_per_100g,
        )
        self._ensure_unique_name(product.name)
        self._products.append(product)
        self._next_id += 1
        return product

    def update_product(
        self,
        product_id: int,
        name: str,
        kcal_per_100g: float,
        protein_per_100g: float,
        fat_per_100g: float,
        carbs_per_100g: float,
    ) -> Product:
        """Заменить название и пищевую ценность продукта с этим id.

        Идентификатор и положение в каталоге сохраняются. Проверки те же,
        что при добавлении. Своё прежнее название, в том числе в другом
        регистре, дубликатом не считается. Если продукта нет, каталог
        не меняется.
        """
        product_id = _require_id(product_id)
        index = self._index_of(product_id)
        if index is None:
            raise ValueError("продукт не найден")

        updated = Product(
            id=product_id,
            name=name,
            kcal_per_100g=kcal_per_100g,
            protein_per_100g=protein_per_100g,
            fat_per_100g=fat_per_100g,
            carbs_per_100g=carbs_per_100g,
        )
        self._ensure_unique_name(updated.name, except_id=product_id)
        self._products[index] = updated
        return updated

    def remove_product(self, product_id: int) -> Product:
        """Удалить продукт с этим id и вернуть его.

        Остальные продукты сохраняют идентификаторы и взаимный порядок.
        """
        product_id = _require_id(product_id)
        index = self._index_of(product_id)
        if index is None:
            raise ValueError("продукт не найден")
        return self._products.pop(index)

    def find_by_name(self, query: str) -> tuple[Product, ...]:
        """Найти продукты по названию без учёта регистра.

        Сначала идут точные совпадения названия, затем продукты, в названии
        которых запрос встречается как подстрока. Внутри каждой группы
        сохраняется порядок каталога. Пробелы по краям запроса не учитываются.
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

    def _index_of(self, product_id: int) -> int | None:
        for index, product in enumerate(self._products):
            if product.id == product_id:
                return index
        return None

    def _ensure_unique_name(self, name: str, *, except_id: int | None = None) -> None:
        key = name.casefold()
        for product in self._products:
            if product.id == except_id:
                continue
            if product.name.casefold() == key:
                raise ValueError("продукт с таким названием уже есть")


def _require_id(product_id: object) -> int:
    """Тот же отказ, что у Product: id — целое число, но не bool."""
    if isinstance(product_id, bool) or not isinstance(product_id, int):
        raise ValueError("id должен быть целым числом")
    return product_id
