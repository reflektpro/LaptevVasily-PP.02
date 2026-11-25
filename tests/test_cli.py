"""Проверка консольного меню."""

from calorie_calc import ProductCatalog
from calorie_calc.cli import run


def _run_menu(monkeypatch, capsys, answers, catalog=None) -> str:
    items = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(items))
    run(catalog if catalog is not None else ProductCatalog())
    return capsys.readouterr().out


def _csv(tmp_path):
    path = tmp_path / "products.csv"
    path.write_text(
        "name,kcal,protein,fat,carbs\n"
        "Яблоко,52,0.3,0.2,14\n"
        "Хлеб,250,8,3,50\n"
        ",1,1,1,1\n",
        encoding="utf-8",
    )
    return path


def test_exit(monkeypatch, capsys):
    out = _run_menu(monkeypatch, capsys, ["0"])
    assert "Импорт продуктов" in out


def test_unknown_item(monkeypatch, capsys):
    out = _run_menu(monkeypatch, capsys, ["9", "0"])
    assert "Неизвестный пункт меню." in out


def test_import_reports_count_and_errors(monkeypatch, capsys, tmp_path):
    out = _run_menu(monkeypatch, capsys, ["1", str(_csv(tmp_path)), "0"])
    assert "Загружено продуктов: 2." in out
    assert "Строка 4:" in out


def test_import_missing_file(monkeypatch, capsys, tmp_path):
    out = _run_menu(monkeypatch, capsys, ["1", str(tmp_path / "no.csv"), "0"])
    assert "Не удалось открыть файл." in out


def test_search(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    out = _run_menu(monkeypatch, capsys, ["2", "ябл", "2", "сыр", "0"], catalog)
    assert "Яблоко: 52.0 ккал на 100 г" in out
    assert "Ничего не найдено." in out


def test_portion(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    out = _run_menu(monkeypatch, capsys, ["3", "хлеб", "200", "0"], catalog)
    assert "500.0 ккал, белки 16.0 г, жиры 6.0 г, углеводы 100.0 г" in out


def test_portion_invalid_mass(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    out = _run_menu(monkeypatch, capsys, ["3", "хлеб", "0", "0"], catalog)
    assert "Ошибка:" in out


def test_diary_and_total(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    answers = [
        "4", "хлеб", "100", "завтрак",
        "4", "яблоко", "200", "перекус",
        "5", "0",
    ]
    out = _run_menu(monkeypatch, capsys, answers, catalog)
    assert out.count("Запись добавлена.") == 2
    assert "завтрак: Хлеб, 100 г" in out
    assert "Итого за день: 354.0 ккал" in out


def test_diary_invalid_meal(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    out = _run_menu(
        monkeypatch, capsys, ["4", "хлеб", "100", "полдник", "5", "0"], catalog
    )
    assert "Ошибка:" in out
    assert "Рацион пуст." in out


def test_export_csv_and_reload(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    catalog.add_product("Сыр", 350, 25, 27, 0)
    target = tmp_path / "out.csv"
    out = _run_menu(monkeypatch, capsys, ["6", str(target), "0"], catalog)
    assert f"Сохранено продуктов: 3 в файл {target}." in out
    names = [product.name for product in ProductCatalog(target).products]
    assert names == ["Яблоко", "Хлеб", "Сыр"]


def test_export_json_then_import(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    target = tmp_path / "out.JSON"
    answers = ["6", str(target), "1", str(target), "2", "хлеб", "0"]
    out = _run_menu(monkeypatch, capsys, answers, catalog)
    assert "Сохранено продуктов: 2" in out
    assert "Загружено продуктов: 2." in out
    assert "Хлеб: 250.0 ккал на 100 г" in out


def test_export_unsupported_format(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    target = tmp_path / "out.txt"
    out = _run_menu(monkeypatch, capsys, ["6", str(target), "0"], catalog)
    assert "Поддерживаются только файлы .csv и .json." in out
    assert not target.exists()


def test_export_unwritable_path(monkeypatch, capsys, tmp_path):
    catalog = ProductCatalog(_csv(tmp_path))
    target = tmp_path / "missing_dir" / "out.csv"
    out = _run_menu(monkeypatch, capsys, ["6", str(target), "0"], catalog)
    assert "Не удалось сохранить файл." in out
