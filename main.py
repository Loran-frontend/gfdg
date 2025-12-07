from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = "ТУТ_ТВОЙ_ТОКЕН"
app = Flask(__name__)

active_codes = {}
used_codes = {}

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.json
    code = data.get("code")
    if code:
        active_codes[code] = True
        print(f"[INFO] Добавлен код: {code}")
        return "OK"
    return "ERROR", 400

@app.route('/check_code', methods=['GET'])
def check_code():
    code = request.args.get("code")
    if code in used_codes:
        telegram_id = used_codes.pop(code)
        active_codes.pop(code, None)
        return str(telegram_id)
    return "NONE"

@app.route('/remove_code', methods=['POST'])
def remove_code():
    data = request.json
    code = data.get("code")
    if code:
        active_codes.pop(code, None)
        used_codes.pop(code, None)
        return "OK"
    return "ERROR", 400

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id

    if text in active_codes:
        used_codes[text] = telegram_id
        await update.message.reply_text("Код принят! ID отправлен серверу.")
    else:
        await update.message.reply_text("Код не найден или уже использован.")

async def run_bot():
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    await app_tg.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    app.run(host="0.0.0.0", port=8080)
