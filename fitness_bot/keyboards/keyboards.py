# keyboards/keyboards.py — Reply-клавиатуры Telegram

def main_menu() -> dict:
    return {
        "keyboard": [
            ["📊 Мой профиль", "💬 Обратная связь"],
            ["💪 Тренировки", "🍎 Питание"],
            ["😴 Сон", "🏋️ Упражнения"],
            ["🔧 Настройки"]
        ],
        "resize_keyboard": True
    }

def workouts_menu() -> dict:
    return {
        "keyboard": [
            ["📅 Сегодня", "📆 План на месяц"],
            ["🏆 Мои рекорды", "📝 Моё расписание"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def nutrition_menu() -> dict:
    return {
        "keyboard": [
            ["🍽️ Сегодня", "📆 План питания на месяц"],
            ["🥗 Рецепты"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def sleep_menu() -> dict:
    return {
        "keyboard": [
            ["😴 Записать сон", "📊 Статистика сна"],
            ["📈 График сна", "🎯 Норма сна"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def exercises_menu() -> dict:
    return {
        "keyboard": [
            ["💪 Выбрать группу мышц"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def settings_menu() -> dict:
    return {
        "keyboard": [
            ["✏️ Изменить профиль", "🏠 Режим тренировок"],
            ["🎯 Цель по сну", "📤 Экспорт данных"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def build_inline(buttons: list) -> dict:
    """
    Создать inline-клавиатуру.
    buttons = [("Текст", "callback_data"), ...]
    """
    return {
        "inline_keyboard": [[{"text": t, "callback_data": d}] for t, d in buttons]
    }
