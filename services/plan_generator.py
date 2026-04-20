# services/plan_generator.py — генерация плана тренировок на месяц

import datetime
from services.ai_service import ask_ai

def generate_monthly_plan(user: dict) -> str:
    """Сгенерировать план тренировок на 30 дней через ИИ."""
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

Для каждого дня укажи реальную дату и конкретные упражнения (название, подходы × повторения).
Дни отдыха обозначь явно. Формат: "ДД.ММ.YYYY — [описание]".
"""
    return ask_ai(prompt)

def generate_nutrition_plan(user: dict) -> str:
    """Сгенерировать план питания на месяц."""
    today = datetime.date.today().strftime("%d.%m.%Y")
    prompt = f"""
Составь план питания на 30 дней начиная с {today}.
Профиль:
- Вес: {user.get('weight', '—')} кг, рост: {user.get('height', '—')} см
- Цель: {user.get('goal', 'здоровое питание')}
- Ограничения: {user.get('restrictions', 'нет')}

Для каждого дня укажи примерный рацион (завтрак, обед, ужин, перекус) с КБЖУ.
"""
    return ask_ai(prompt)

def get_today_workout(user: dict, plan_text: str) -> str:
    """Вытащить из плана тренировку на сегодня."""
    today = datetime.date.today().strftime("%d.%m.%Y")
    if today in plan_text:
        lines = plan_text.split("\n")
        result = []
        capture = False
        for line in lines:
            if today in line:
                capture = True
            elif capture and line.strip().startswith("0") or (capture and "." in line[:6]):
                break
            if capture:
                result.append(line)
        return "\n".join(result).strip() or f"Тренировка на {today} не найдена в плане."
    return f"📅 Тренировка на {today}: план ещё не сгенерирован. Нажмите «📆 План на месяц»."
