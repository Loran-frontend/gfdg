import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot

# --- Настройки ---
TOKEN = "8394612560:AAEA_-8I-TMpW7LxCEmGHBu8uWa6FMoHcJk"
if not TOKEN:
    raise ValueError("Установите переменную окружения TOKEN")

PORT = int(os.environ.get("PORT", 5000))
PUBLIC_URL = "https://gfdg-production.up.railway.app"  # Обязательно HTTPS
if not PUBLIC_URL:
    raise ValueError("Установите переменную окружения PUBLIC_URL")

WEBHOOK_PATH = f"/{TOKEN}"  # защищённый путь webhook

# --- Инициализация ---
app = Flask(__name__)
bot = Bot(token=TOKEN)

# --- Хранилища кодов ---
active_codes = {}
used_codes = {}

# --- Flask API для работы с кодами ---
@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.json
    if not data or "code" not in data:
        return "ERROR: Missing 'code'", 400
    code = data["code"]
    active_codes[code] = True
    print(f"[INFO] Добавлен код: {code}")
    return "OK"

@app.route('/check_code', methods=['GET'])
def check_code():
    code = request.args.get("code")
    if not code:
        return "ERROR: Missing 'code' param", 400
    if code in used_codes:
        telegram_id = used_codes.pop(code)
        active_codes.pop(code, None)
        return str(telegram_id)
    return "NONE"

@app.route('/remove_code', methods=['POST'])
def remove_code():
    data = request.json
    if not data or "code" not in data:
        return "ERROR: Missing 'code'", 400
    code = data["code"]
    active_codes.pop(code, None)
    used_codes.pop(code, None)
    print(f"[INFO] Код {code} удалён")
    return "OK"

# --- Telegram webhook endpoint ---
@app.route(WEBHOOK_PATH, methods=['POST'])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    # Запускаем обработку сообщений в отдельной задаче asyncio
    asyncio.create_task(handle_update(update))
    return "OK"

# --- Асинхронная обработка сообщений ---
async def handle_update(update: Update):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id

    if text in active_codes:
        used_codes[text] = telegram_id
        await bot.send_message(
            chat_id=telegram_id,
            text="Код принят! Ваш Telegram ID будет привязан к Minecraft аккаунту."
        )
        print(f"[INFO] Код {text} использован пользователем {telegram_id}")
    else:
        await bot.send_message(
            chat_id=telegram_id,
            text="Код не найден или уже использован."
        )

# --- Запуск Flask и установка webhook ---
if __name__ == "__main__":
    webhook_url = f"{PUBLIC_URL}{WEBHOOK_PATH}"
    bot.set_webhook(webhook_url)
    print(f"[INFO] Webhook установлен: {webhook_url}")
    app.run(host="0.0.0.0", port=PORT)
