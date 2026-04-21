# handlers/router.py — основной диспетчер сообщений

import json
import datetime
from config import ADMIN_ID, FEEDBACK_FORM_URL
from db import user_repo
from db.measurements import add_sleep, add_weight, get_sleep_avg, get_sleep_history
from db.exercises import get_muscle_groups, get_exercises_by_group
from db.recipes import get_cuisines, get_categories, get_recipes, get_recipe_by_id
from services.ai_service import ask_ai
from services.plan_generator import (
    generate_monthly_plan, generate_nutrition_plan, get_today_workout
)
from services.chart_service import build_sleep_chart
from services.export_service import export_user_data
from handlers.state import (
    set_state, get_state, clear_state,
    save_workout_plan, get_workout_plan,
    save_nutrition_plan, get_nutrition_plan
)
from keyboards.keyboards import (
    main_menu, workouts_menu, nutrition_menu,
    sleep_menu, exercises_menu, settings_menu, build_inline
)
from utils.telegram import send_message, send_photo, send_document, answer_callback
from utils.regex_handlers import (
    parse_sleep, parse_weight_change, parse_record, parse_add_exercise
)


# ── Вспомогательные функции ──────────────────────────────────────────

def _profile_text(u: dict) -> str:
    records = u.get("records") or {}
    recs_text = "\n".join(
        f"  • {ex}: {v.get('weight')} кг × {v.get('reps')} раз"
        for ex, v in records.items()
    ) or "  нет рекордов"
    return (
        f"<b>👤 Профиль</b>\n"
        f"Имя: {u.get('name', '—')}\n"
        f"Возраст: {u.get('age', '—')} лет\n"
        f"Вес: {u.get('weight', '—')} кг\n"
        f"Рост: {u.get('height', '—')} см\n"
        f"Цель: {u.get('goal', '—')}\n"
        f"Режим: {u.get('training_mode', 'зал')}\n"
        f"Спорт: {u.get('sport_type', 'фитнес')}\n"
        f"Норма сна: {u.get('sleep_target', 8)} ч\n\n"
        f"<b>🏆 Рекорды:</b>\n{recs_text}"
    )


# ── Главный диспетчер ────────────────────────────────────────────────

def handle_update(update: dict):
    print(f"[handle_update] keys: {list(update.keys())}") 
    
    if "callback_query" in update:
        cq = update["callback_query"]
        answer_callback(cq["id"])
        handle_callback(cq)
        return

    message = update.get("message", {})
    if not message:
        return

    chat_id = message["chat"]["id"]
    user_id = chat_id
    text = message.get("text", "").strip()

    if not text:
        return

    # Убедиться, что пользователь существует
    user = user_repo.get_user(user_id)

    # ── Команды ──
    if text == "/start":
        handle_start(chat_id, user_id, message)
        return
    if text == "/admin" and user_id == ADMIN_ID:
        handle_admin(chat_id)
        return

    # ── Натуральные команды (regex) ──
    if parsed := parse_sleep(text):
        add_sleep(user_id, parsed)
        send_message(chat_id, f"😴 Записал: {parsed} ч сна.", main_menu())
        return
    if parsed := parse_weight_change(text):
        user_repo.update_user(user_id, {"weight": parsed})
        add_weight(user_id, parsed)
        send_message(chat_id, f"⚖️ Вес обновлён: {parsed} кг.", main_menu())
        return
    if parsed := parse_record(text):
        if user:
            records = user.get("records") or {}
            records[parsed["exercise"]] = {"weight": parsed["weight"], "reps": parsed["reps"]}
            user_repo.update_user(user_id, {"records": records})
            send_message(chat_id,
                f"🏆 Рекорд сохранён!\n{parsed['exercise']}: "
                f"{parsed['weight']} кг × {parsed.get('reps', '—')} раз", main_menu())
        return
    if parsed := parse_add_exercise(text):
        if user:
            custom = user.get("custom_exercises") or {}
            custom[parsed] = True
            user_repo.update_user(user_id, {"custom_exercises": custom})
            send_message(chat_id, f"✅ Упражнение «{parsed}» добавлено в ваш список.", main_menu())
        return

    # ── Состояния (мультишаговые диалоги) ──
    state = get_state(user_id)
    step = state.get("step", "")

    if step:
        handle_state(chat_id, user_id, text, step, state.get("data", {}), user)
        return

    # ── Кнопки меню ──
    handle_menu(chat_id, user_id, text, user)


# ── /start ───────────────────────────────────────────────────────────

def handle_start(chat_id, user_id, message):
    first_name = message["chat"].get("first_name", "друг")
    user = user_repo.get_user(user_id)
    if not user:
        user_repo.create_user(user_id, first_name)
        set_state(user_id, "onboarding_age")
        send_message(chat_id,
            f"👋 Привет, <b>{first_name}</b>! Я твой AI-тренер по фитнесу.\n\n"
            f"Давай познакомимся. Сколько тебе лет?")
    else:
        send_message(chat_id,
            f"👋 Привет снова, <b>{user.get('name', first_name)}</b>!\n"
            f"Чем могу помочь?", main_menu())


# ── Онбординг и состояния ─────────────────────────────────────────────

def handle_state(chat_id, user_id, text, step, data, user):
    """Обработка пошаговых диалогов."""

    # Онбординг
    if step == "onboarding_age":
        try:
            age = int(text)
            user_repo.update_user(user_id, {"age": age})
            set_state(user_id, "onboarding_weight")
            send_message(chat_id, "⚖️ Отлично! Какой у тебя вес (кг)?")
        except ValueError:
            send_message(chat_id, "Введи число, например: 25")

    elif step == "onboarding_weight":
        try:
            weight = float(text.replace(",", "."))
            user_repo.update_user(user_id, {"weight": weight})
            set_state(user_id, "onboarding_height")
            send_message(chat_id, "📏 Какой рост (см)?")
        except ValueError:
            send_message(chat_id, "Введи число, например: 75")

    elif step == "onboarding_height":
        try:
            height = float(text.replace(",", "."))
            user_repo.update_user(user_id, {"height": height})
            set_state(user_id, "onboarding_goal")
            send_message(chat_id,
                "🎯 Какая твоя цель?\nНапример: похудение, набор массы, выносливость, здоровье")
        except ValueError:
            send_message(chat_id, "Введи число, например: 175")

    elif step == "onboarding_goal":
        user_repo.update_user(user_id, {"goal": text})
        clear_state(user_id)
        send_message(chat_id,
            "✅ <b>Профиль создан!</b> Теперь я смогу составлять персональные планы.\n\n"
            "Выбери раздел:", main_menu())

    # Запись сна
    elif step == "input_sleep":
        try:
            hours = float(text.replace(",", "."))
            add_sleep(user_id, hours)
            clear_state(user_id)
            send_message(chat_id, f"✅ Записал: {hours} ч сна.", sleep_menu())
        except ValueError:
            send_message(chat_id, "Введи число, например: 7.5")

    # Изменение нормы сна
    elif step == "set_sleep_target":
        try:
            t = float(text.replace(",", "."))
            user_repo.update_user(user_id, {"sleep_target": t})
            clear_state(user_id)
            send_message(chat_id, f"✅ Норма сна обновлена: {t} ч", sleep_menu())
        except ValueError:
            send_message(chat_id, "Введи число, например: 8")

    # Изменение веса
    elif step == "update_weight":
        try:
            w = float(text.replace(",", "."))
            user_repo.update_user(user_id, {"weight": w})
            add_weight(user_id, w)
            clear_state(user_id)
            send_message(chat_id, f"✅ Вес обновлён: {w} кг", settings_menu())
        except ValueError:
            send_message(chat_id, "Введи число, например: 72")

    # Изменение роста
    elif step == "update_height":
        try:
            h = float(text.replace(",", "."))
            user_repo.update_user(user_id, {"height": h})
            clear_state(user_id)
            send_message(chat_id, f"✅ Рост обновлён: {h} см", settings_menu())
        except ValueError:
            send_message(chat_id, "Введи число, например: 175")

    # Изменение цели
    elif step == "update_goal":
        user_repo.update_user(user_id, {"goal": text})
        clear_state(user_id)
        send_message(chat_id, f"✅ Цель обновлена: {text}", settings_menu())

    # Изменение режима тренировок
    elif step == "update_training_mode":
        user_repo.update_user(user_id, {"training_mode": text})
        clear_state(user_id)
        send_message(chat_id, f"✅ Режим обновлён: {text}", settings_menu())

    # Расписание
    elif step == "set_schedule":
        try:
            schedule = json.loads(text)
        except Exception:
            schedule = text  # сохраняем как строку
        user_repo.update_user(user_id, {"custom_schedule": schedule})
        clear_state(user_id)
        send_message(chat_id, "✅ Расписание сохранено!", workouts_menu())

    # Добавление рекорда (пошагово)
    elif step == "add_record_exercise":
        set_state(user_id, "add_record_weight", {"exercise": text})
        send_message(chat_id, f"💪 Упражнение: {text}\nВведи вес (кг):")

    elif step == "add_record_weight":
        try:
            w = float(text.replace(",", "."))
            data["weight"] = w
            set_state(user_id, "add_record_reps", data)
            send_message(chat_id, "Введи количество повторений:")
        except ValueError:
            send_message(chat_id, "Введи число, например: 100")

    elif step == "add_record_reps":
        try:
            reps = int(text)
            u = user_repo.get_user(user_id)
            records = u.get("records") or {}
            records[data["exercise"]] = {"weight": data["weight"], "reps": reps}
            user_repo.update_user(user_id, {"records": records})
            clear_state(user_id)
            send_message(chat_id,
                f"🏆 Рекорд сохранён!\n{data['exercise']}: {data['weight']} кг × {reps} раз",
                workouts_menu())
        except ValueError:
            send_message(chat_id, "Введи число, например: 8")

    else:
        clear_state(user_id)
        handle_menu(chat_id, user_id, text, user)


# ── Меню ─────────────────────────────────────────────────────────────

def handle_menu(chat_id, user_id, text, user):
    """Обработка нажатий кнопок меню."""

    # Главное меню
    if text == "📊 Мой профиль":
        if not user:
            send_message(chat_id, "Сначала введи /start", main_menu())
            return
        send_message(chat_id, _profile_text(user), main_menu())

    elif text == "💬 Обратная связь":
        msg = "💬 <b>Обратная связь</b>\n"
        if FEEDBACK_FORM_URL:
            msg += f'<a href="{FEEDBACK_FORM_URL}">Оставить отзыв</a>'
        else:
            msg += "Пиши напрямую: @admin"
        send_message(chat_id, msg, main_menu())

    # Тренировки
    elif text == "💪 Тренировки":
        send_message(chat_id, "💪 <b>Тренировки</b>", workouts_menu())

    elif text == "📅 Сегодня":
        plan = get_workout_plan(user_id)
        msg = get_today_workout(user, plan)
        send_message(chat_id, f"📅 <b>Тренировка сегодня</b>\n\n{msg}", workouts_menu())

    elif text == "📆 План на месяц":
        if not user:
            send_message(chat_id, "Сначала введи /start")
            return
        send_message(chat_id, "⏳ Генерирую план... (может занять до 30 сек)")
        plan = generate_monthly_plan(user)
        save_workout_plan(user_id, plan)
        for i in range(0, len(plan), 4000):
            send_message(chat_id, plan[i:i+4000])
        send_message(chat_id, "✅ План сохранён!", workouts_menu())

    elif text == "🏆 Мои рекорды":
        if user:
            records = user.get("records") or {}
            if records:
                lines = [f"• {ex}: {v.get('weight')} кг × {v.get('reps', '—')} раз"
                         for ex, v in records.items()]
                buttons = [(f"❌ {ex}", f"del_record:{ex}") for ex in records]
                buttons.append(("➕ Добавить рекорд", "add_record"))
                send_message(chat_id,
                    "🏆 <b>Рекорды:</b>\n" + "\n".join(lines),
                    build_inline(buttons))
            else:
                send_message(chat_id, "Рекордов пока нет.",
                    build_inline([("➕ Добавить рекорд", "add_record")]))

    elif text == "📝 Моё расписание":
        if user:
            sched = user.get("custom_schedule") or "не задано"
            send_message(chat_id,
                f"📝 <b>Текущее расписание:</b>\n{sched}\n\n"
                "Отправь новое расписание (текстом или JSON):")
            set_state(user_id, "set_schedule")

    # Питание
    elif text == "🍎 Питание":
        send_message(chat_id, "🍎 <b>Питание</b>", nutrition_menu())

    elif text == "🍽️ Сегодня":
        if not user:
            return
        send_message(chat_id, "⏳ Составляю рекомендации...")
        today = datetime.date.today().strftime("%d.%m.%Y")
        prompt = (f"Дай рекомендацию по питанию на {today} для человека: "
                  f"вес {user.get('weight')} кг, цель: {user.get('goal')}. "
                  f"Завтрак, обед, ужин с КБЖУ.")
        answer = ask_ai(prompt)
        send_message(chat_id, f"🍽️ <b>Питание на сегодня:</b>\n\n{answer}", nutrition_menu())

    elif text in ("📆 План питания на месяц", "🎯 План питания"):
        if not user:
            return
        send_message(chat_id, "⏳ Генерирую план питания...")
        plan = generate_nutrition_plan(user)
        save_nutrition_plan(user_id, plan)
        for i in range(0, len(plan), 4000):
            send_message(chat_id, plan[i:i+4000])
        send_message(chat_id, "✅ План питания готов!", nutrition_menu())

    elif text == "🥗 Рецепты":
        cuisines = get_cuisines()
        if cuisines:
            buttons = [(c, f"cuisine:{c}") for c in cuisines]
            send_message(chat_id, "🌍 Выбери кухню:", build_inline(buttons))
        else:
            send_message(chat_id, "Рецепты не найдены. Проверь базу данных.", nutrition_menu())

    # Сон
    elif text == "😴 Сон":
        send_message(chat_id, "😴 <b>Сон</b>", sleep_menu())

    elif text == "😴 Записать сон":
        set_state(user_id, "input_sleep")
        send_message(chat_id, "Сколько часов ты спал(а)? Введи число (например: 7.5):")

    elif text == "📊 Статистика сна":
        avg = get_sleep_avg(user_id, 7)
        target = (user or {}).get("sleep_target", 8)
        diff = round(avg - target, 1)
        emoji = "✅" if diff >= 0 else "⚠️"
        send_message(chat_id,
            f"😴 <b>Статистика сна (7 дней)</b>\n\n"
            f"Среднее: <b>{avg} ч</b>\n"
            f"Норма: <b>{target} ч</b>\n"
            f"{emoji} Разница: {'+' if diff >= 0 else ''}{diff} ч", sleep_menu())

    elif text == "📈 График сна":
        records = get_sleep_history(user_id, 30)
        if not records:
            send_message(chat_id, "Данных о сне пока нет.", sleep_menu())
            return
        target = (user or {}).get("sleep_target", 8)
        chart = build_sleep_chart(records, target)
        send_photo(chat_id, chart, "📈 График сна за 30 дней")

    elif text == "🎯 Норма сна":
        target = (user or {}).get("sleep_target", 8)
        send_message(chat_id,
            f"🎯 Текущая норма сна: <b>{target} ч</b>\n\nВведи новую норму:")
        set_state(user_id, "set_sleep_target")

    # Упражнения
    elif text == "🏋️ Упражнения":
        send_message(chat_id, "🏋️ <b>Упражнения</b>", exercises_menu())

    elif text == "💪 Выбрать группу мышц":
        groups = get_muscle_groups()
        if groups:
            buttons = [(g, f"muscle:{g}") for g in groups]
            send_message(chat_id, "Выбери группу мышц:", build_inline(buttons))
        else:
            send_message(chat_id, "Каталог пуст. Добавь упражнения в таблицу exercises_catalog.")

    # Настройки
    elif text == "🔧 Настройки":
        send_message(chat_id, "🔧 <b>Настройки</b>", settings_menu())

    elif text == "✏️ Изменить профиль":
        send_message(chat_id, "Что изменить?", build_inline([
            ("⚖️ Вес", "upd:weight"),
            ("📏 Рост", "upd:height"),
            ("🎯 Цель", "upd:goal"),
            ("🏠 Режим тренировок", "upd:training_mode"),
        ]))

    elif text == "📤 Экспорт данных":
        csv_bytes = export_user_data(user_id)
        send_document(chat_id, csv_bytes, "my_fitness_data.csv",
                      "📤 Твои данные (вес, сон)")
        send_message(chat_id, "✅ Экспорт готов!", settings_menu())

    elif text == "🔙 Назад":
        send_message(chat_id, "Главное меню:", main_menu())

    else:
        # Неизвестная команда — AI-ответ
        if user:
            answer = ask_ai(
                f"Пользователь написал: «{text}». Ответь как фитнес-тренер кратко.",
            )
            send_message(chat_id, answer, main_menu())
        else:
            send_message(chat_id, "Введи /start для начала.", main_menu())


# ── Callback-запросы ─────────────────────────────────────────────────

def handle_callback(cq: dict):
    chat_id = cq["message"]["chat"]["id"]
    user_id = chat_id
    data = cq.get("data", "")
    print(f"[callback] chat_id={chat_id} data={data}") 
    user = user_repo.get_user(user_id)

    if data == "add_record":
        set_state(user_id, "add_record_exercise")
        send_message(chat_id, "Введи название упражнения:")

    elif data.startswith("del_record:"):
        exercise = data.split(":", 1)[1]
        if user:
            records = user.get("records") or {}
            records.pop(exercise, None)
            user_repo.update_user(user_id, {"records": records})
            send_message(chat_id, f"✅ Рекорд «{exercise}» удалён.", workouts_menu())

    elif data.startswith("cuisine:"):
        cuisine = data.split(":", 1)[1]
        categories = get_categories(cuisine)
        buttons = [(c, f"cat:{cuisine}:{c}") for c in categories]
        send_message(chat_id, f"📂 Категории кухни «{cuisine}»:", build_inline(buttons))

    elif data.startswith("cat:"):
        _, cuisine, category = data.split(":", 2)
        recipes = get_recipes(cuisine, category)
        buttons = [(r["name"], f"recipe:{r['id']}") for r in recipes]
        send_message(chat_id, f"🍽️ Блюда «{category}»:", build_inline(buttons))

    elif data.startswith("recipe:"):
        recipe_id = int(data.split(":")[1])
        r = get_recipe_by_id(recipe_id)
        if r:
            text = (f"<b>🍽️ {r['name']}</b>\n\n"
                    f"<b>Ингредиенты:</b>\n{r['ingredients']}\n\n"
                    f"<b>Приготовление:</b>\n{r['instructions']}")
            send_message(chat_id, text[:4000], nutrition_menu())

    elif data.startswith("muscle:"):
        group = data.split(":", 1)[1]
        # Получаем режим тренировок пользователя
        training_mode = (user or {}).get("training_mode", "зал")
    
        # Маппинг режимов — дом и турники видят своё + базовые
        mode_filter = {
            "зал": ["зал"],
            "дом": ["дом"],
            "турники": ["турники", "дом"],  # турники видят и домашние тоже
        }
        allowed_modes = mode_filter.get(training_mode, ["зал"])
    
        all_exercises = get_exercises_by_group(group)
        exercises = [e for e in all_exercises if e.get("training_mode") in allowed_modes]
    
    if exercises:
        lines = [f"• {e['name']}" for e in exercises]
        text = (f"<b>💪 {group}</b> — режим: {training_mode}\n\n" + "\n".join(lines))
        send_message(chat_id, text, exercises_menu())
    else:
         send_message(chat_id,
            f"Для режима «{training_mode}» упражнений по группе «{group}» не найдено.",
             exercises_menu())

 elif data.startswith("upd:"):
        field = data.split(":")[1]
        prompts = {
            "weight": ("⚖️ Введи новый вес (кг):", "update_weight"),
            "height": ("📏 Введи новый рост (см):", "update_height"),
            "goal": ("🎯 Введи новую цель:", "update_goal"),
            "training_mode": ("🏠 Введи режим (дом / турники / зал):", "update_training_mode"),
        }
        if field in prompts:
            msg, step = prompts[field]
            set_state(user_id, step)
            send_message(chat_id, msg)


# ── Админ-команда ────────────────────────────────────────────────────

def handle_admin(chat_id):
    all_users = user_repo.get_all_users()
    now = datetime.datetime.utcnow()
    day_ago = (now - datetime.timedelta(days=1)).isoformat()
    month_ago = (now - datetime.timedelta(days=30)).isoformat()
    active_day = sum(1 for u in all_users if u.get("last_active", "") >= day_ago)
    active_month = sum(1 for u in all_users if u.get("last_active", "") >= month_ago)
    send_message(chat_id,
        f"<b>📊 Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{len(all_users)}</b>\n"
        f"🔥 Активны за сутки: <b>{active_day}</b>\n"
        f"📅 Активны за месяц: <b>{active_month}</b>")
