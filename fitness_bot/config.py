# config.py — все настройки и переменные окружения

import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# OpenRouter (GPT-4o mini)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openai/gpt-4o-mini"

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Прочее
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
FEEDBACK_FORM_URL = os.getenv("FEEDBACK_FORM_URL", "")
PORT = int(os.getenv("PORT", "10000"))

# Кэш пользователей: время жизни в секундах (1 час)
USER_CACHE_TTL = 3600
