# services/ai_service.py — запросы к OpenRouter

import requests
from config import OPENROUTER_API_KEY, OPENROUTER_URL, AI_MODEL

def ask_ai(prompt: str, system: str = "Ты — профессиональный AI-тренер по фитнесу.") -> str:
    """Отправить запрос к OpenRouter и вернуть текст ответа."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 2000,
    }
    try:
        res = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {e}"
