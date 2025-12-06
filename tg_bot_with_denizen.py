from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from threading import Thread

TOKEN = ""
app = Flask(__name__)

active_codes = {}
used_codes = {}

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
        print(f"[INFO] Код {code} удалён")
        return "OK"
    return "ERROR", 400

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

if __name__ == "__main__":
    Thread(target=lambda: app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling()
