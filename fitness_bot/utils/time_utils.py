# utils/time_utils.py — работа с московским временем

import datetime
import zoneinfo

MOSCOW_TZ = zoneinfo.ZoneInfo("Europe/Moscow")

def now_moscow() -> datetime.datetime:
    return datetime.datetime.now(tz=MOSCOW_TZ)

def today_moscow() -> datetime.date:
    return now_moscow().date()

def format_date(dt: datetime.date) -> str:
    return dt.strftime("%d.%m.%Y")
