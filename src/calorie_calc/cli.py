"""Консольное меню: импорт, поиск, порция, рацион, норма, экспорт и правка каталога."""

from calorie_calc.catalog import ProductCatalog
from calorie_calc.csv_import import CsvRowError
from calorie_calc.json_import import JsonItemError
from calorie_calc.diary import MEAL_TYPES, MealEntry, total_nutrients
from calorie_calc.models import PortionNutrients, Product
from calorie_calc.norm import ACTIVITY_LEVELS, compare_with_norm, daily_norm

MENU = """
1. Импорт продуктов из файла (CSV или JSON)
2. Поиск продукта
3. Расчёт порции
4. Добавить в рацион
5. Показать рацион и итог за день
6. Экспорт каталога в файл (CSV или JSON)
7. Добавить продукт в каталог
8. Удалить продукт из каталога
9. Изменить продукт в каталоге
10. Дневная норма и сравнение с рационом
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


def _add_product(catalog: ProductCatalog) -> None:
    """Спросить название и КБЖУ на 100 г и добавить продукт в каталог."""
    name = input("Название продукта: ")
    try:
        kcal = _read_number(input("Калорийность на 100 г, ккал: "))
        protein = _read_number(input("Белки на 100 г, г: "))
        fat = _read_number(input("Жиры на 100 г, г: "))
        carbs = _read_number(input("Углеводы на 100 г, г: "))
        product = catalog.add_product(name, kcal, protein, fat, carbs)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print(f"Продукт «{product.name}» добавлен (id {product.id}).")


def _remove_product(catalog: ProductCatalog) -> None:
    """Найти продукт по названию и удалить его после подтверждения."""
    product = _choose_product(catalog)
    if product is None:
        return
    answer = input(f"Удалить «{product.name}»? (д/н): ").strip().lower()
    if answer not in ("д", "да", "y", "yes"):
        print("Удаление отменено.")
        return
    catalog.remove_product(product.id)
    print(f"Продукт «{product.name}» удалён.")


def _ask_value(prompt: str, current: float) -> float:
    """Спросить число; пустой ввод оставляет текущее значение."""
    text = input(f"{prompt} [{current:g}]: ").strip()
    if not text:
        return current
    return _read_number(text)


def _edit_product(catalog: ProductCatalog) -> None:
    """Найти продукт по названию и изменить его название и КБЖУ на 100 г.

    Пустой ввод оставляет прежнее значение поля.
    """
    product = _choose_product(catalog)
    if product is None:
        return
    name = input(f"Новое название [{product.name}]: ").strip() or product.name
    try:
        kcal = _ask_value("Калорийность на 100 г, ккал", product.kcal_per_100g)
        protein = _ask_value("Белки на 100 г, г", product.protein_per_100g)
        fat = _ask_value("Жиры на 100 г, г", product.fat_per_100g)
        carbs = _ask_value("Углеводы на 100 г, г", product.carbs_per_100g)
        updated = catalog.update_product(product.id, name, kcal, protein, fat, carbs)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print(
        f"Продукт «{updated.name}» изменён: {updated.kcal_per_100g:g} ккал на 100 г "
        f"(Б {updated.protein_per_100g:g}, Ж {updated.fat_per_100g:g}, "
        f"У {updated.carbs_per_100g:g})."
    )


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


def _norm(diary: list[MealEntry]) -> None:
    """Рассчитать дневную норму калорий и сравнить с ней рацион за день."""
    sex = input("Пол (м/ж): ")
    try:
        weight = _read_number(input("Вес, кг: "))
        height = _read_number(input("Рост, см: "))
        age = int(input("Возраст, лет: ").strip())
        activity = input(f"Активность ({', '.join(ACTIVITY_LEVELS)}): ")
        norm = daily_norm(sex, weight, height, age, activity)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    eaten = total_nutrients(diary).kcal
    result = compare_with_norm(eaten, norm)
    print(f"Дневная норма: {norm:g} ккал. Съедено: {eaten:g} ккал.")
    if result["status"] == "остаток":
        print(f"До нормы осталось {result['remaining']:g} ккал.")
    elif result["status"] == "перебор":
        print(f"Норма превышена на {result['excess']:g} ккал.")
    else:
        print("Съедено ровно по норме.")


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
        elif choice == "7":
            _add_product(catalog)
        elif choice == "8":
            _remove_product(catalog)
        elif choice == "9":
            _edit_product(catalog)
        elif choice == "10":
            _norm(diary)
        else:
            print("Неизвестный пункт меню.")
