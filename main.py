from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio
import threading
import os

TOKEN = "ТВОЙ_ТОКЕН"
app = Flask(__name__)

active_codes = {}
used_codes = {}

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/add_code", methods=["POST"])
def add_code():
    code = request.json.get("code")
    if code:
        active_codes[code] = True
        print(f"[INFO] Added code: {code}")
        return "OK"
    return "ERROR", 400

@app.route("/check_code", methods=["GET"])
def check_code():
    code = request.args.get("code")
    if code in used_codes:
        telegram_id = used_codes.pop(code)
        active_codes.pop(code, None)
        return str(telegram_id)
    return "NONE"

@app.route("/remove_code", methods=["POST"])
def remove_code():
    code = request.json.get("code")
    if code:
        active_codes.pop(code, None)
        used_codes.pop(code, None)
        print(f"[INFO] Code removed: {code}")
        return "OK"
    return "ERROR", 400

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id

    if text in active_codes:
        used_codes[text] = telegram_id
        await update.message.reply_text("Код принят! Аккаунт будет привязан.")
        print(f"[INFO] Code {text} used by {telegram_id}")
    else:
        await update.message.reply_text("Код не найден или уже использован.")

async def start_bot_async():
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # <--- ВАЖНО: отключаем сигналы
    await app_tg.run_polling(
        stop_signals=None,
        close_loop=False
    )

def start_bot():
    asyncio.run(start_bot_async())

if __name__ == "__main__":
    # Стартуем Telegram-бота в отдельном потоке
    threading.Thread(target=start_bot, daemon=True).start()

    # Flask запускаем как обычный Railway backend
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
