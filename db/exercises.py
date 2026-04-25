# db/exercises.py — каталог упражнений и персональные списки

from db.client import get_client


def get_muscle_groups() -> list:
    """Получить уникальные группы мышц."""
    try:
        res = get_client().table("exercises_catalog").select("muscle_group").execute()
        groups = list({r["muscle_group"] for r in res.data}) if res.data else []
        print(f"[exercises] muscle groups: {groups}")
        return sorted(groups)
    except Exception as e:
        print(f"[exercises error] get_muscle_groups: {e}")
        return []


def get_exercises_by_group(muscle_group: str) -> list:
    """Все упражнения по группе мышц из каталога."""
    try:
        res = get_client().table("exercises_catalog") \
            .select("*").eq("muscle_group", muscle_group).execute()
        return res.data or []
    except Exception as e:
        print(f"[exercises error] get_exercises_by_group: {e}")
        return []


def get_user_all_exercise_ids(user_id: int) -> dict:
    """Получить все записи пользователя {exercise_id: is_active}."""
    try:
        res = get_client().table("user_exercises") \
            .select("exercise_id, is_active") \
            .eq("user_id", user_id) \
            .execute()
        return {r["exercise_id"]: r["is_active"] for r in res.data} if res.data else {}
    except Exception as e:
        print(f"[exercises error] get_user_all_exercise_ids: {e}")
        return {}


def toggle_user_exercise(user_id: int, exercise_id: int) -> bool:
    """
    Переключить упражнение для пользователя.
    Если нет записи — создаёт активную.
    Если есть — переключает is_active.
    Возвращает новое состояние is_active.
    """
    try:
        client = get_client()
        res = client.table("user_exercises") \
            .select("id, is_active") \
            .eq("user_id", user_id) \
            .eq("exercise_id", exercise_id) \
            .execute()

        if res.data:
            current = res.data[0]["is_active"]
            new_state = not current
            client.table("user_exercises") \
                .update({"is_active": new_state}) \
                .eq("user_id", user_id) \
                .eq("exercise_id", exercise_id) \
                .execute()
            return new_state
        else:
            client.table("user_exercises").insert({
                "user_id": user_id,
                "exercise_id": exercise_id,
                "is_active": True
            }).execute()
            return True
    except Exception as e:
        print(f"[exercises error] toggle_user_exercise: {e}")
        return False


def get_exercise_name(exercise_id: int) -> str:
    """Получить название упражнения по ID."""
    try:
        res = get_client().table("exercises_catalog") \
            .select("name").eq("id", exercise_id).execute()
        return res.data[0]["name"] if res.data else f"Упражнение #{exercise_id}"
    except Exception as e:
        print(f"[exercises error] get_exercise_name: {e}")
        return f"Упражнение #{exercise_id}"


def get_all_exercises() -> list:
    """Все упражнения из каталога."""
    try:
        res = get_client().table("exercises_catalog").select("*").execute()
        return res.data or []
    except Exception as e:
        print(f"[exercises error] get_all_exercises: {e}")
        return []
