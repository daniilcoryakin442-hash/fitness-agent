# 🏋️ AI Fitness Bot

Telegram-бот «AI-тренер по фитнесу» на Python + Flask + Supabase + OpenRouter.

## Структура проекта

```
fitness_bot/
├── app.py                  # Точка входа Flask, вебхук
├── config.py               # Все настройки и переменные окружения
├── requirements.txt
├── supabase_schema.sql     # SQL для создания таблиц
├── .env.example            # Пример переменных окружения
├── db/
│   ├── client.py           # Подключение к Supabase
│   ├── user_repo.py        # Работа с пользователями (кэш, CRUD)
│   ├── measurements.py     # Вес, сон
│   ├── exercises.py        # Каталог упражнений
│   └── recipes.py          # Рецепты
├── services/
│   ├── ai_service.py       # Запросы к OpenRouter
│   ├── plan_generator.py   # Генерация планов
│   ├── chart_service.py    # График сна (matplotlib)
│   ├── export_service.py   # Экспорт в CSV
│   └── state_manager.py    # Заглушка
├── handlers/
│   ├── router.py           # Основной диспетчер
│   └── state.py            # In-memory состояния
├── keyboards/
│   └── keyboards.py        # Reply и inline клавиатуры
└── utils/
    ├── time_utils.py       # Московское время
    ├── regex_handlers.py   # Парсинг команд
    └── telegram.py         # Отправка сообщений
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируй .env своими данными
```

### 3. Создание таблиц в Supabase

Открой **Supabase → SQL Editor** и выполни содержимое файла `supabase_schema.sql`.

### 4. Запуск локально

```bash
export $(cat .env | xargs)
python app.py
```

Для тестирования вебхука локально используй [ngrok](https://ngrok.com/):

```bash
ngrok http 10000
# Зарегистрируй вебхук:
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=https://ТВОЙ-NGROK-URL/webhook"
```

## Деплой на Render

1. Создай новый **Web Service** на [render.com](https://render.com)
2. Подключи репозиторий с кодом
3. Настройки сервиса:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Добавь переменные окружения в раздел **Environment**
5. После деплоя зарегистрируй вебхук:

```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<ИМЯ-СЕРВИСА>.onrender.com/webhook"
```

## Функции бота

| Раздел | Функции |
|--------|---------|
| 💪 Тренировки | Тренировка на сегодня, план на месяц, рекорды, расписание |
| 🍎 Питание | Питание на день, план на месяц, рецепты по кухням |
| 😴 Сон | Запись сна, статистика, график, норма |
| 🏋️ Упражнения | Каталог по группам мышц |
| 🔧 Настройки | Профиль, режим тренировок, экспорт CSV |

### Натуральные команды (regex)
- `спал 7.5 часов` — записать сон
- `изменить вес на 72 кг` — обновить вес
- `установить рекорд жим лёжа 100 кг на 8 раз` — сохранить рекорд
- `добавить упражнение подтягивания` — добавить в личный список
