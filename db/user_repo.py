# db/user_repo.py — CRUD для пользователей с кэшированием в памяти

import time
from db.client import get_client
from config import USER_CACHE_TTL

# Кэш: {user_id: {"data": {...}, "ts": timestamp}}
_cache: dict = {}

def get_user(user_id: int) -> dict | None:
    """Получить пользователя из кэша или Supabase."""
    now = time.time()
    if user_id in _cache and now - _cache[user_id]["ts"] < USER_CACHE_TTL:
        return _cache[user_id]["data"]

    res = get_client().table("users").select("*").eq("user_id", user_id).execute()
    if res.data:
        _cache[user_id] = {"data": res.data[0], "ts": now}
        return res.data[0]
    return None

def create_user(user_id: int, name: str) -> dict:
    """Создать нового пользователя."""
    data = {"user_id": user_id, "name": name}
    res = get_client().table("users").insert(data).execute()
    user = res.data[0]
    _cache[user_id] = {"data": user, "ts": time.time()}
    return user

def update_user(user_id: int, fields: dict) -> dict:
    """Обновить поля пользователя."""
    import datetime
    fields["last_active"] = datetime.datetime.utcnow().isoformat()
    res = get_client().table("users").update(fields).eq("user_id", user_id).execute()
    if res.data:
        _cache[user_id] = {"data": res.data[0], "ts": time.time()}
        return res.data[0]
    return {}

def invalidate_cache(user_id: int):
    """Удалить пользователя из кэша."""
    _cache.pop(user_id, None)

def get_all_users() -> list:
    """Получить всех пользователей (для админа)."""
    res = get_client().table("users").select("*").execute()
    return res.data or []
