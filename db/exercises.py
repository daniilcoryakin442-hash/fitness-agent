# db/exercises.py — каталог упражнений и рекорды

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
    """Упражнения по группе мышц."""
    try:
        res = get_client().table("exercises_catalog")\
            .select("*").eq("muscle_group", muscle_group).execute()
        return res.data or []
    except Exception as e:
        print(f"[exercises error] get_exercises_by_group: {e}")
        return []

def get_all_exercises() -> list:
    """Все упражнения из каталога."""
    try:
        res = get_client().table("exercises_catalog").select("*").execute()
        return res.data or []
    except Exception as e:
        print(f"[exercises error] get_all_exercises: {e}")
        return []
