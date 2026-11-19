"""Проверка экспорта дневного отчёта."""

import csv

import pytest

from calorie_calc import (
    MealEntry,
    Product,
    export_report_csv,
    export_report_text,
)


def _entries():
    milk = Product(1, "Молоко", 52, 2.8, 2.5, 4.7)
    bread = Product(2, "Хлеб", 250, 8, 3, 50)
    return [MealEntry(milk, 200, "завтрак"), MealEntry(bread, 100, "обед")]


def test_text_report(tmp_path):
    path = export_report_text(_entries(), tmp_path / "report.txt")
    text = path.read_text(encoding="utf-8")
    assert "завтрак: Молоко, 200 г" in text
    assert "Итого: 354.0 ккал" in text


def test_text_report_empty(tmp_path):
    path = export_report_text([], tmp_path / "report.txt")
    text = path.read_text(encoding="utf-8")
    assert "Записей нет" in text
    assert "Итого: 0.0 ккал" in text


def test_csv_report(tmp_path):
    path = export_report_csv(_entries(), tmp_path / "report.csv")
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    assert rows[0][0] == "приём пищи"
    assert len(rows) == 4
    assert rows[1][:3] == ["завтрак", "Молоко", "200"]
    assert rows[-1][0] == "итого"
    assert float(rows[-1][3]) == 354.0


def test_invalid_entry(tmp_path):
    with pytest.raises(ValueError):
        export_report_csv(["не запись"], tmp_path / "r.csv")
    with pytest.raises(ValueError):
        export_report_text([1], tmp_path / "r.txt")
