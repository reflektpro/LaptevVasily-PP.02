"""Проверка импорта продуктов из CSV."""

from pathlib import Path

from calorie_calc import Product, import_products
from calorie_calc.csv_import import import_products as import_products_impl

_PRODUCTS_CSV = Path(__file__).resolve().parents[1] / "data" / "products.csv"

# name, kcal, protein, fat, carbs — как в data/products.csv
_BUNDLED_ROWS = (
    ("Овсяные хлопья", 379, 13.0, 6.5, 67.0),
    ("Гречневая крупа", 313, 12.6, 3.3, 62.1),
    ("Рис белый", 344, 6.7, 0.7, 78.9),
    ("Пшено", 348, 11.5, 3.3, 69.3),
    ("Макароны", 338, 10.4, 1.1, 71.5),
    ("Хлеб ржаной", 174, 6.6, 1.2, 33.4),
    ("Хлеб пшеничный", 235, 7.6, 0.8, 49.2),
    ("Картофель", 77, 2.0, 0.4, 16.3),
    ("Морковь", 35, 1.3, 0.1, 6.9),
    ("Капуста белокочанная", 27, 1.8, 0.1, 4.7),
    ("Свёкла", 43, 1.5, 0.1, 8.8),
    ("Помидор", 20, 0.9, 0.2, 3.9),
    ("Огурец", 15, 0.8, 0.1, 2.5),
    ("Лук репчатый", 41, 1.4, 0.0, 8.2),
    ("Яблоко", 52, 0.3, 0.2, 14.0),
    ("Банан", 89, 1.1, 0.3, 22.8),
    ("Апельсин", 43, 0.9, 0.2, 8.1),
    ("Куриная грудка", 113, 23.6, 1.9, 0.4),
    ("Говядина", 187, 18.9, 12.4, 0.0),
    ("Свинина", 259, 16.0, 21.6, 0.0),
    ("Минтай", 72, 15.9, 0.9, 0.0),
    ("Яйцо куриное", 157, 12.7, 11.5, 0.7),
    ("Молоко 2.5%", 52, 2.8, 2.5, 4.7),
    ("Творог 5%", 121, 17.2, 5.0, 1.8),
    ("Кефир 1%", 40, 3.0, 1.0, 4.0),
    ("Сыр российский", 363, 23.2, 30.0, 0.0),
)


def test_import_products_exported_from_package() -> None:
    import calorie_calc

    assert import_products is import_products_impl
    assert calorie_calc.__version__ == "0.6.0"


def test_import_products_maps_columns_and_assigns_ids(tmp_path: Path) -> None:
    csv_path = tmp_path / "products.csv"
    csv_path.write_text(
        "protein,name,carbs,kcal,fat\n"
        "13.0,  Овсянка  ,67,379,6.5\n"
        "0,Вода,0,0,0\n",
        encoding="utf-8",
    )

    products = import_products(str(csv_path))

    assert products == [
        Product(
            id=1,
            name="Овсянка",
            kcal_per_100g=379,
            protein_per_100g=13.0,
            fat_per_100g=6.5,
            carbs_per_100g=67,
        ),
        Product(
            id=2,
            name="Вода",
            kcal_per_100g=0,
            protein_per_100g=0,
            fat_per_100g=0,
            carbs_per_100g=0,
        ),
    ]


def test_import_products_header_only_returns_empty_list(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("name,kcal,protein,fat,carbs\n", encoding="utf-8")

    assert import_products(csv_path) == []


def test_import_bundled_products_csv() -> None:
    products = import_products(_PRODUCTS_CSV)

    assert len(products) == len(_BUNDLED_ROWS) == 26
    assert [product.id for product in products] == list(range(1, 27))
    assert all(isinstance(product, Product) for product in products)

    for product, (name, kcal, protein, fat, carbs) in zip(
        products, _BUNDLED_ROWS, strict=True
    ):
        assert product.name == name
        assert product.kcal_per_100g == float(kcal)
        assert product.protein_per_100g == float(protein)
        assert product.fat_per_100g == float(fat)
        assert product.carbs_per_100g == float(carbs)
