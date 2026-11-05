"""Проверка, что каркас пакета импортируется."""


def test_package_imports() -> None:
    import calorie_calc

    assert calorie_calc.__version__
