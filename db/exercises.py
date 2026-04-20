# db/exercises.py — каталог упражнений и рекорды

from db.client import get_client

def get_muscle_groups() -> list:
    """Получить уникальные группы мышц."""
    res = get_client().table("exercises_catalog").select("muscle_group").execute()
    groups = list({r["muscle_group"] for r in res.data}) if res.data else []
    return sorted(groups)

def get_exercises_by_group(muscle_group: str) -> list:
    """Упражнения по группе мышц."""
    res = get_client().table("exercises_catalog")\
        .select("*").eq("muscle_group", muscle_group).execute()
    return res.data or []

def get_all_exercises() -> list:
    """Все упражнения из каталога."""
    res = get_client().table("exercises_catalog").select("*").execute()
    return res.data or []
