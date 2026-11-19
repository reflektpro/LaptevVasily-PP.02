"""Экспорт дневного отчёта в текстовый или CSV файл."""

import csv
from pathlib import Path

from calorie_calc.diary import MealEntry, total_nutrients

CSV_HEADER = ["приём пищи", "продукт", "масса, г", "ккал", "белки", "жиры", "углеводы"]


def _check(entries) -> list:
    entries = list(entries)
    for entry in entries:
        if not isinstance(entry, MealEntry):
            raise ValueError("ожидается запись рациона")
    return entries


def export_report_text(entries, path) -> Path:
    """Сохраняет отчёт за день в текстовый файл (UTF-8)."""
    entries = _check(entries)
    total = total_nutrients(entries)
    lines = ["Отчёт за день", ""]
    for entry in entries:
        item = entry.nutrients()
        lines.append(
            f"{entry.meal}: {entry.product.name}, {entry.grams:g} г — "
            f"{item.kcal} ккал, Б {item.protein}, Ж {item.fat}, У {item.carbs}"
        )
    if not entries:
        lines.append("Записей нет")
    lines.append("")
    lines.append(
        f"Итого: {total.kcal} ккал, Б {total.protein}, "
        f"Ж {total.fat}, У {total.carbs}"
    )
    path = Path(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def export_report_csv(entries, path) -> Path:
    """Сохраняет отчёт за день в CSV файл (UTF-8, разделитель «,»)."""
    entries = _check(entries)
    total = total_nutrients(entries)
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        for entry in entries:
            item = entry.nutrients()
            writer.writerow(
                [entry.meal, entry.product.name, f"{entry.grams:g}",
                 item.kcal, item.protein, item.fat, item.carbs]
            )
        writer.writerow(
            ["итого", "", "", total.kcal, total.protein, total.fat, total.carbs]
        )
    return path
