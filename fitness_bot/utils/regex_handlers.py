# utils/regex_handlers.py — парсинг натуральных команд

import re

def parse_sleep(text: str) -> float | None:
    """'спал 7.5 часов' → 7.5"""
    m = re.search(r"спал[а]?\s+([\d.,]+)\s*час", text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", "."))
    return None

def parse_weight_change(text: str) -> float | None:
    """'изменить вес на 72 кг' → 72.0"""
    m = re.search(r"(?:изменить|обновить|вес|установить вес)[^\d]*([\d.,]+)\s*кг", text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", "."))
    return None

def parse_record(text: str) -> dict | None:
    """
    'установить рекорд жим лёжа 100 кг на 8 раз'
    → {"exercise": "жим лёжа", "weight": 100.0, "reps": 8}
    """
    m = re.search(
        r"(?:установить|новый|рекорд)\s+рекорд\s+(.+?)\s+([\d.,]+)\s*кг(?:\s+на\s+(\d+)\s+раз)?",
        text, re.IGNORECASE
    )
    if m:
        return {
            "exercise": m.group(1).strip(),
            "weight": float(m.group(2).replace(",", ".")),
            "reps": int(m.group(3)) if m.group(3) else None
        }
    return None

def parse_add_exercise(text: str) -> str | None:
    """'добавить упражнение подтягивания' → 'подтягивания'"""
    m = re.search(r"добавить упражнение\s+(.+)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None
