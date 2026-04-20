# utils/telegram.py — отправка сообщений и фото через Telegram Bot API

import requests
import json
from config import TELEGRAM_API

def send_message(chat_id: int, text: str, reply_markup=None, parse_mode: str = "HTML"):
    """Отправить текстовое сообщение."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"[send_message error] {e}")

def send_photo(chat_id: int, photo_bytes: bytes, caption: str = ""):
    """Отправить фото из байтов."""
    try:
        requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("chart.png", photo_bytes, "image/png")},
            timeout=15
        )
    except Exception as e:
        print(f"[send_photo error] {e}")

def send_document(chat_id: int, file_bytes: bytes, filename: str, caption: str = ""):
    """Отправить файл (например CSV)."""
    try:
        requests.post(
            f"{TELEGRAM_API}/sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (filename, file_bytes, "text/csv")},
            timeout=15
        )
    except Exception as e:
        print(f"[send_document error] {e}")

def answer_callback(callback_query_id: str):
    """Ответить на callback-запрос (убрать часики)."""
    requests.post(f"{TELEGRAM_API}/answerCallbackQuery",
                  json={"callback_query_id": callback_query_id}, timeout=5)
