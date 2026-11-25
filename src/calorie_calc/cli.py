"""Консольное меню: импорт, поиск, порция, рацион, экспорт каталога."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.csv_import import CsvRowError
from calorie_calc.json_import import JsonItemError
from calorie_calc.diary import MEAL_TYPES, MealEntry, total_nutrients
from calorie_calc.models import PortionNutrients, Product

MENU = """
1. Импорт продуктов из файла (CSV или JSON)
2. Поиск продукта
3. Расчёт порции
4. Добавить в рацион
5. Показать рацион и итог за день
6. Экспорт каталога в файл (CSV или JSON)
0. Выход"""


def _read_number(text: str) -> float:
    return float(text.replace(",", "."))


def _format_nutrients(item: PortionNutrients) -> str:
    return (
        f"{item.kcal} ккал, белки {item.protein} г, "
        f"жиры {item.fat} г, углеводы {item.carbs} г"
    )


def _choose_product(catalog: ProductCatalog) -> Product | None:
    """Спросить название и вернуть найденный продукт."""
    found = catalog.find_by_name(input("Название продукта: "))
    if not found:
        print("Продукт не найден.")
        return None
    if len(found) == 1:
        return found[0]
    for number, product in enumerate(found, start=1):
        print(f"{number}. {product.name}")
    try:
        return found[int(input("Номер из списка: ")) - 1]
    except (ValueError, IndexError):
        print("Неверный номер.")
        return None


def _import(catalog: ProductCatalog) -> ProductCatalog:
    path = input("Путь к файлу CSV или JSON: ").strip()
    errors: list[CsvRowError | JsonItemError] = []
    try:
        new_catalog = ProductCatalog(path, errors)
    except ValueError:
        print("Поддерживаются только файлы .csv и .json.")
        return catalog
    except OSError:
        print("Не удалось открыть файл.")
        return catalog
    print(f"Загружено продуктов: {len(new_catalog)}.")
    for error in errors:
        if isinstance(error, JsonItemError):
            print(f"Элемент {error.item}: {error.message}")
        else:
            print(f"Строка {error.line}: {error.message}")
    return new_catalog


def _export(catalog: ProductCatalog) -> None:
    """Сохранить текущий каталог (с изменениями) в CSV или JSON."""
    path = input("Путь к файлу CSV или JSON для сохранения: ").strip()
    try:
        saved = catalog.save(path)
    except ValueError:
        print("Поддерживаются только файлы .csv и .json.")
        return
    except OSError:
        print("Не удалось сохранить файл.")
        return
    print(f"Сохранено продуктов: {len(catalog)} в файл {saved}.")


def _search(catalog: ProductCatalog) -> None:
    found = catalog.find_by_name(input("Запрос: "))
    if not found:
        print("Ничего не найдено.")
    for product in found:
        print(
            f"{product.name}: {product.kcal_per_100g} ккал на 100 г "
            f"(Б {product.protein_per_100g}, Ж {product.fat_per_100g}, "
            f"У {product.carbs_per_100g})"
        )


def _portion(catalog: ProductCatalog) -> None:
    product = _choose_product(catalog)
    if product is None:
        return
    try:
        grams = _read_number(input("Масса, г: "))
        print(_format_nutrients(catalog.calculate_portion(product, grams)))
    except ValueError as error:
        print(f"Ошибка: {error}")


def _add_to_diary(catalog: ProductCatalog, diary: list[MealEntry]) -> None:
    product = _choose_product(catalog)
    if product is None:
        return
    try:
        grams = _read_number(input("Масса, г: "))
        meal = input(f"Приём пищи ({', '.join(MEAL_TYPES)}): ")
        diary.append(MealEntry(product, grams, meal))
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print("Запись добавлена.")


def _show_diary(diary: list[MealEntry]) -> None:
    if not diary:
        print("Рацион пуст.")
        return
    for entry in diary:
        print(f"{entry.meal}: {entry.product.name}, {entry.grams:g} г")
    print("Итого за день: " + _format_nutrients(total_nutrients(diary)))


def run(catalog: ProductCatalog | None = None) -> None:
    """Цикл меню до выбора пункта «Выход»."""
    if catalog is None:
        catalog = ProductCatalog()
    diary: list[MealEntry] = []
    while True:
        print(MENU)
        choice = input("Пункт меню: ").strip()
        if choice == "0":
            break
        if choice == "1":
            catalog = _import(catalog)
        elif choice == "2":
            _search(catalog)
        elif choice == "3":
            _portion(catalog)
        elif choice == "4":
            _add_to_diary(catalog, diary)
        elif choice == "5":
            _show_diary(diary)
        elif choice == "6":
            _export(catalog)
        else:
            print("Неизвестный пункт меню.")
