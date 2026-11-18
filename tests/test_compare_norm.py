import pytest

from calorie_calc.norm import compare_with_norm


def test_remaining():
    result = compare_with_norm(1500, 2000)
    assert result == {"remaining": 500, "excess": 0.0, "status": "остаток"}


def test_excess():
    result = compare_with_norm(2300.5, 2000)
    assert result["excess"] == 300.5
    assert result["remaining"] == 0.0
    assert result["status"] == "перебор"


def test_exact():
    assert compare_with_norm(2000, 2000)["status"] == "в норме"


def test_zero_eaten():
    assert compare_with_norm(0, 1800)["remaining"] == 1800


@pytest.mark.parametrize("eaten, norm", [(-1, 2000), (100, 0), (100, -5),
                                          ("100", 2000), (100, None),
                                          (True, 2000)])
def test_invalid(eaten, norm):
    with pytest.raises(ValueError):
        compare_with_norm(eaten, norm)
