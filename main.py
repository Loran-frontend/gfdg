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
        await update.message.reply_text("Код принят! Система привяжет ваш аккаунт.")
        print(f"[INFO] Code {text} used by {telegram_id}")
    else:
        await update.message.reply_text("Код не найден или уже использован.")

def start_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    loop.run_until_complete(application.run_polling())

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
