import pytest

from calorie_calc.norm import ACTIVITY_LEVELS, daily_norm


def test_man_norm():
    # 10*80 + 6.25*180 - 5*30 + 5 = 1780; * 1.55
    assert daily_norm("м", 80, 180, 30, "средняя") == 2759.0


def test_woman_norm():
    # 10*60 + 6.25*165 - 5*25 - 161 = 1345.25; * 1.2
    assert daily_norm("ж", 60, 165, 25, "минимальная") == 1614.3


def test_text_is_normalized():
    assert daily_norm(" М ", 80, 180, 30, " Средняя ") == 2759.0


def test_all_levels_known():
    for level in ACTIVITY_LEVELS:
        assert daily_norm("м", 70, 175, 20, level) > 0


@pytest.mark.parametrize("args", [
    ("x", 70, 175, 20, "средняя"),
    ("м", 0, 175, 20, "средняя"),
    ("м", 70, -1, 20, "средняя"),
    ("м", 70, 175, 0, "средняя"),
    ("м", "70", 175, 20, "средняя"),
    ("м", 70, 175, 20, "космическая"),
])
def test_invalid_input(args):
    with pytest.raises(ValueError):
        daily_norm(*args)
