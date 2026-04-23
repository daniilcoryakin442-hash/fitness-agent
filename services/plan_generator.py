# services/plan_generator.py

import datetime
from services.ai_service import ask_ai

def generate_monthly_plan(user: dict) -> str:
    today = datetime.date.today().strftime("%d.%m.%Y")
    schedule = user.get("custom_schedule") or "не задано"
    prompt = f"""
Составь подробный план тренировок на 30 дней начиная с {today}.
Профиль пользователя:
- Имя: {user.get('name', 'Пользователь')}
- Возраст: {user.get('age', '—')} лет
- Вес: {user.get('weight', '—')} кг, рост: {user.get('height', '—')} см
- Цель: {user.get('goal', 'общая физическая форма')}
- Режим тренировок: {user.get('training_mode', 'зал')}
- Вид спорта: {user.get('sport_type', 'фитнес')}
- Желаемые повторения: {user.get('target_reps', 8)}
- Расписание: {schedule}

ВАЖНО: Каждый день начинай строго с даты в формате ДД.ММ.YYYY в начале строки.
Пример формата:
24.04.2026 — Грудь + трицепс
- Жим штанги лёжа: 4×8
- Жим гантелей: 3×10
- Отжимания на брусьях: 3×12

25.04.2026 — ОТДЫХ

Дни отдыха обозначай как "ОТДЫХ". Не пропускай ни одной даты.
"""
    return ask_ai(prompt)

def generate_nutrition_plan(user: dict) -> str:
    today = datetime.date.today().strftime("%d.%m.%Y")
    prompt = f"""
Составь план питания на 30 дней начиная с {today}.
Профиль:
- Вес: {user.get('weight', '—')} кг, рост: {user.get('height', '—')} см
- Цель: {user.get('goal', 'здоровое питание')}
- Ограничения: {user.get('restrictions', 'нет')}

ВАЖНО: Каждый день начинай строго с даты в формате ДД.ММ.YYYY.
Для каждого дня: завтрак, обед, ужин, перекус с КБЖУ.
"""
    return ask_ai(prompt)

def get_today_workout(user: dict, plan_text: str) -> str:
    """Найти тренировку на сегодня из плана."""
    if not plan_text:
        return "📅 План ещё не сгенерирован. Нажми «📆 План на месяц»."

    today = datetime.date.today().strftime("%d.%m.%Y")

    # Ищем строку с сегодняшней датой
    lines = plan_text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(today):
            start_idx = i
            break

    if start_idx is None:
        return (f"📅 Тренировка на {today} не найдена в плане.\n\n"
                f"Возможно план устарел — нажми «📆 План на месяц» чтобы создать новый.")

    # Собираем строки до следующей даты
    result = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        # Следующая дата — останавливаемся
        if i > start_idx and len(line) >= 10 and line[2:3] == "." and line[5:6] == ".":
            break
        result.append(line)

    workout = "\n".join(result).strip()

    if "ОТДЫХ" in workout.upper():
        return f"😴 {today} — день отдыха! Восстанавливайся и набирайся сил."

    return workout
