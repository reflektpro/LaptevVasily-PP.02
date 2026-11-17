"""Дневная норма калорий по формуле Миффлина — Сан-Жеора."""

ACTIVITY_LEVELS = {
    "минимальная": 1.2,
    "низкая": 1.375,
    "средняя": 1.55,
    "высокая": 1.725,
    "очень высокая": 1.9,
}


def daily_norm(sex: str, weight: float, height: float, age: int,
               activity: str) -> float:
    """Возвращает норму калорий в сутки (ккал).

    sex — «м» или «ж», weight — вес в кг, height — рост в см,
    age — возраст в годах, activity — уровень активности из ACTIVITY_LEVELS.
    """
    if not isinstance(sex, str) or sex.strip().lower() not in ("м", "ж"):
        raise ValueError("пол должен быть «м» или «ж»")
    for value in (weight, height, age):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("вес, рост и возраст должны быть числами")
        if value <= 0:
            raise ValueError("вес, рост и возраст должны быть больше нуля")
    if not isinstance(activity, str):
        raise ValueError("активность должна быть строкой")
    key = activity.strip().lower()
    if key not in ACTIVITY_LEVELS:
        raise ValueError("неизвестный уровень активности")

    base = 10 * weight + 6.25 * height - 5 * age
    if sex.strip().lower() == "м":
        base += 5
    else:
        base -= 161
    return round(base * ACTIVITY_LEVELS[key], 2)
