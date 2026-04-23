# handlers/state.py — in-memory состояния диалогов + сохранение планов в Supabase

from db.client import get_client

# Структура: {user_id: {"step": "...", "data": {...}}}
_states: dict = {}

# Локальный кэш планов (чтобы не дёргать базу каждый раз)
_workout_cache: dict = {}
_nutrition_cache: dict = {}


def set_state(user_id: int, step: str, data: dict = None):
    _states[user_id] = {"step": step, "data": data or {}}

def get_state(user_id: int) -> dict:
    return _states.get(user_id, {})

def clear_state(user_id: int):
    _states.pop(user_id, None)


# ── Планы тренировок ──────────────────────────────────────────────────

def save_workout_plan(user_id: int, plan: str):
    """Сохранить план тренировок в Supabase и кэш."""
    _workout_cache[user_id] = plan
    try:
        get_client().table("workout_plans").upsert({
            "user_id": user_id,
            "plan_text": plan,
        }).execute()
        print(f"[state] workout plan saved for {user_id}")
    except Exception as e:
        print(f"[state] error saving workout plan: {e}")

def get_workout_plan(user_id: int) -> str:
    """Получить план тренировок из кэша или Supabase."""
    if user_id in _workout_cache:
        return _workout_cache[user_id]
    try:
        res = get_client().table("workout_plans").select("plan_text")\
            .eq("user_id", user_id).execute()
        if res.data:
            plan = res.data[0]["plan_text"]
            _workout_cache[user_id] = plan
            return plan
    except Exception as e:
        print(f"[state] error loading workout plan: {e}")
    return ""


# ── Планы питания ─────────────────────────────────────────────────────

def save_nutrition_plan(user_id: int, plan: str):
    """Сохранить план питания в Supabase и кэш."""
    _nutrition_cache[user_id] = plan
    try:
        get_client().table("nutrition_plans").upsert({
            "user_id": user_id,
            "plan_text": plan,
        }).execute()
        print(f"[state] nutrition plan saved for {user_id}")
    except Exception as e:
        print(f"[state] error saving nutrition plan: {e}")

def get_nutrition_plan(user_id: int) -> str:
    """Получить план питания из кэша или Supabase."""
    if user_id in _nutrition_cache:
        return _nutrition_cache[user_id]
    try:
        res = get_client().table("nutrition_plans").select("plan_text")\
            .eq("user_id", user_id).execute()
        if res.data:
            plan = res.data[0]["plan_text"]
            _nutrition_cache[user_id] = plan
            return plan
    except Exception as e:
        print(f"[state] error loading nutrition plan: {e}")
    return ""
