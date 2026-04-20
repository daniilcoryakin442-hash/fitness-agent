# handlers/state.py — in-memory состояния диалогов

# Структура: {user_id: {"step": "...", "data": {...}}}
_states: dict = {}

# Кэш сгенерированных планов тренировок: {user_id: "текст плана"}
_workout_plans: dict = {}

# Кэш планов питания: {user_id: "текст плана"}
_nutrition_plans: dict = {}

def set_state(user_id: int, step: str, data: dict = None):
    _states[user_id] = {"step": step, "data": data or {}}

def get_state(user_id: int) -> dict:
    return _states.get(user_id, {})

def clear_state(user_id: int):
    _states.pop(user_id, None)

def save_workout_plan(user_id: int, plan: str):
    _workout_plans[user_id] = plan

def get_workout_plan(user_id: int) -> str:
    return _workout_plans.get(user_id, "")

def save_nutrition_plan(user_id: int, plan: str):
    _nutrition_plans[user_id] = plan

def get_nutrition_plan(user_id: int) -> str:
    return _nutrition_plans.get(user_id, "")
