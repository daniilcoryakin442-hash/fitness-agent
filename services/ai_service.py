# services/ai_service.py — запросы к Google Gemini

import requests
from config import GEMINI_API_KEY

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = "Ты — профессиональный AI-тренер по фитнесу. Отвечай на русском языке."


def ask_ai(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Отправить запрос к Google Gemini и вернуть текст ответа."""
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system}\n\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
        }
    }
    try:
        res = requests.post(
            GEMINI_URL,
            json=payload,
            headers=headers,
            params=params,
            timeout=60
        )
        res.raise_for_status()
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[gemini error] {e}")
        return f"⚠️ Ошибка ИИ: {e}"
