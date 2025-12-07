import os
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update

TOKEN = os.environ.get("TOKEN") or "8394612560:AAEA_-8I-TMpW7LxCEmGHBu8uWa6FMoHcJk"
PORT = int(os.environ.get("PORT", 5000))
PUBLIC_URL = os.environ.get("PUBLIC_URL") or "https://gfdg-production.up.railway.app"
WEBHOOK_PATH = f"/{TOKEN}"

# Хранилища кодов
active_codes = {}
used_codes = {}

app = Flask(__name__)

# --- Telegram обработчик ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id

    if text in active_codes:
        used_codes[text] = telegram_id
        await update.message.reply_text(
            "Код принят! Ваш Telegram ID будет привязан к Minecraft аккаунту."
        )
        print(f"[INFO] Код {text} использован пользователем {telegram_id}")
    else:
        await update.message.reply_text("Код не найден или уже использован.")

# --- Flask API ---
@app.route('/add_code', methods=['POST'])
def add_code():
    data = app.current_request.json_body if hasattr(app, "current_request") else {}
    from flask import request
    data = request.json
    code = data.get("code") if data else None
    if not code:
        return "ERROR: Missing 'code'", 400
    active_codes[code] = True
    print(f"[INFO] Добавлен код: {code}")
    return "OK"

@app.route('/check_code', methods=['GET'])
def check_code():
    from flask import request
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
    from flask import request
    data = request.json
    code = data.get("code") if data else None
    if not code:
        return "ERROR: Missing 'code'", 400
    active_codes.pop(code, None)
    used_codes.pop(code, None)
    print(f"[INFO] Код {code} удалён")
    return "OK"

if __name__ == "__main__":
    # --- Создаём приложение Telegram ---
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # --- Запуск webhook через PTB ---
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{PUBLIC_URL}{WEBHOOK_PATH}",
        # Если нужно использовать свой Flask, можно передать:
        # webhook_app=app
    )
