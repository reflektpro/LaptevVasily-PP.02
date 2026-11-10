"""Точка входа модуля. Логика калькулятора ещё не реализована."""

from calorie_calc import ProductCatalog


def main() -> None:
    catalog = ProductCatalog()
    print(
        "Модуль калькулятора калорий в разработке "
        f"(день 6: каталог, загружено продуктов: {len(catalog)})."
    )


if __name__ == "__main__":
    main()
