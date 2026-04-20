# app.py — точка входа Flask, обработка вебхука

from flask import Flask, request, Response
from config import PORT
from handlers.router import handle_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "✅ Fitness Bot is running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Telegram отправляет апдейты сюда. Сразу возвращаем 200."""
    try:
        update = request.get_json(force=True)
        if update:
            handle_update(update)
    except Exception as e:
        print(f"[webhook error] {e}")
    return Response("ok", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
