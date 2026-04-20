# db/measurements.py — вес и сон

import datetime
from db.client import get_client

def add_weight(user_id: int, weight: float):
    """Записать вес."""
    get_client().table("measurements").insert({
        "user_id": user_id,
        "weight": weight,
        "date": datetime.date.today().isoformat()
    }).execute()

def get_weight_history(user_id: int, days: int = 30) -> list:
    """История веса за N дней."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    res = get_client().table("measurements")\
        .select("*").eq("user_id", user_id)\
        .gte("date", since).order("date").execute()
    return res.data or []

def add_sleep(user_id: int, hours: float):
    """Записать сон."""
    get_client().table("sleep").insert({
        "user_id": user_id,
        "hours": hours,
        "date": datetime.date.today().isoformat()
    }).execute()

def get_sleep_history(user_id: int, days: int = 30) -> list:
    """История сна за N дней."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    res = get_client().table("sleep")\
        .select("*").eq("user_id", user_id)\
        .gte("date", since).order("date").execute()
    return res.data or []

def get_sleep_avg(user_id: int, days: int = 7) -> float:
    """Среднее количество сна за N дней."""
    records = get_sleep_history(user_id, days)
    if not records:
        return 0.0
    return round(sum(r["hours"] for r in records) / len(records), 1)
