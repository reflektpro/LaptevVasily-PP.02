"""Тесты импорта продуктов из JSON (день 18)."""

import json
from pathlib import Path

import pytest

from calorie_calc import (
    JsonItemError,
    import_products,
    import_products_json,
)

DATA = Path(__file__).resolve().parents[1] / "data"


def _write(tmp_path: Path, content: str, name: str = "products.json") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_data_json_matches_csv():
    from_json = import_products_json(DATA / "products.json")
    from_csv = import_products(DATA / "products.csv")
    assert len(from_json) == 26
    assert from_json == from_csv


def test_list_of_objects(tmp_path):
    path = _write(
        tmp_path,
        json.dumps(
            [
                {"name": "Гречка", "kcal": 313, "protein": 12.6, "fat": 3.3, "carbs": 62.1},
                {"name": "Молоко", "kcal": 52, "protein": 2.8, "fat": 2.5, "carbs": 4.7},
            ],
            ensure_ascii=False,
        ),
    )
    products = import_products_json(path)
    assert [p.id for p in products] == [1, 2]
    assert products[0].name == "Гречка"
    assert products[0].kcal_per_100g == 313.0
    assert products[1].carbs_per_100g == 4.7


def test_object_with_products_key_and_extra_fields(tmp_path):
    path = _write(
        tmp_path,
        json.dumps(
            {
                "version": 1,
                "products": [
                    {"name": " Рис ", "kcal": 344, "protein": 6.7, "fat": 0.7,
                     "carbs": 78.9, "category": "крупы"},
                ],
            },
            ensure_ascii=False,
        ),
    )
    products = import_products_json(path)
    assert len(products) == 1
    assert products[0].name == "Рис"


def test_invalid_items_are_skipped_with_errors(tmp_path):
    items = [
        {"name": "Хлеб", "kcal": 242, "protein": 8.1, "fat": 1.0, "carbs": 48.8},
        {"name": "", "kcal": 10, "protein": 1, "fat": 1, "carbs": 1},
        {"name": "Сыр", "kcal": "много", "protein": 1, "fat": 1, "carbs": 1},
        {"name": "Масло", "kcal": 748, "protein": 0.5, "fat": -1, "carbs": 0.8},
        {"name": "Соль", "kcal": True, "protein": 0, "fat": 0, "carbs": 0},
        {"name": "Сахар", "kcal": 399, "protein": 0, "fat": 0},
        "не объект",
        {"name": 5, "kcal": 1, "protein": 1, "fat": 1, "carbs": 1},
        {"name": "Яблоко", "kcal": 47, "protein": 0.4, "fat": 0.4, "carbs": 9.8},
    ]
    path = _write(tmp_path, json.dumps(items, ensure_ascii=False))
    errors: list[JsonItemError] = []
    products = import_products_json(path, errors)

    assert [(p.id, p.name) for p in products] == [(1, "Хлеб"), (2, "Яблоко")]
    assert errors == [
        JsonItemError(2, "не заполнено обязательное поле name"),
        JsonItemError(3, "поле kcal должно быть числом"),
        JsonItemError(4, "поле fat должно быть ≥ 0"),
        JsonItemError(5, "поле kcal должно быть числом"),
        JsonItemError(6, "не заполнено обязательное поле carbs"),
        JsonItemError(7, "элемент должен быть объектом"),
        JsonItemError(8, "поле name должно быть строкой"),
    ]


def test_errors_accumulate_between_calls(tmp_path):
    path = _write(tmp_path, '[{"name": "X"}]')
    errors: list[JsonItemError] = []
    import_products_json(path, errors)
    import_products_json(path, errors)
    assert len(errors) == 8


@pytest.mark.parametrize("content", ["", "   \n", "[]", '{"products": []}'])
def test_empty_inputs_give_empty_list(tmp_path, content):
    errors: list[JsonItemError] = []
    assert import_products_json(_write(tmp_path, content), errors) == []
    assert errors == []


def test_bom_is_skipped(tmp_path):
    path = tmp_path / "bom.json"
    path.write_text(
        '[{"name": "Кефир", "kcal": 40, "protein": 3, "fat": 1, "carbs": 4}]',
        encoding="utf-8-sig",
    )
    assert import_products_json(path)[0].name == "Кефир"


def test_broken_json_gives_file_error(tmp_path):
    errors: list[JsonItemError] = []
    path = _write(tmp_path, '[{"name": "Кефир",\n')
    assert import_products_json(path, errors) == []
    assert len(errors) == 1
    assert errors[0].item == 0
    assert errors[0].message.startswith("некорректный JSON")


@pytest.mark.parametrize("content", ['{"items": []}', '"строка"', "42", '{"products": {}}'])
def test_wrong_structure_gives_file_error(tmp_path, content):
    errors: list[JsonItemError] = []
    assert import_products_json(_write(tmp_path, content), errors) == []
    assert errors == [
        JsonItemError(0, "ожидается список продуктов или объект с ключом products")
    ]


def test_non_utf8_file_gives_file_error(tmp_path):
    path = tmp_path / "cp1251.json"
    path.write_bytes('[{"name": "Сыр"}]'.encode("cp1251"))
    errors: list[JsonItemError] = []
    assert import_products_json(path, errors) == []
    assert errors == [JsonItemError(0, "файл должен быть в кодировке UTF-8")]


def test_nan_and_infinity_rejected(tmp_path):
    path = _write(
        tmp_path,
        '[{"name": "A", "kcal": NaN, "protein": 1, "fat": 1, "carbs": 1},'
        ' {"name": "B", "kcal": 1, "protein": Infinity, "fat": 1, "carbs": 1}]',
    )
    errors: list[JsonItemError] = []
    assert import_products_json(path, errors) == []
    assert errors == [
        JsonItemError(1, "поле kcal должно быть числом"),
        JsonItemError(2, "поле protein должно быть числом"),
    ]
