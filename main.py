import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from threading import Thread

# Получаем токен из переменных окружения
TOKEN = 8394612560:AAEA_-8I-TMpW7LxCEmGHBu8uWa6FMoHcJk
if not TOKEN:
    raise ValueError("Пожалуйста, установите переменную окружения TOKEN")

app = Flask(__name__)

# Хранилища кодов
active_codes = {}
used_codes = {}

# --- Flask эндпоинты ---
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

# --- Telegram бот ---
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

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling()

if __name__ == "__main__":
    # Получаем порт из переменных окружения (Railway)
    port = int(os.environ.get("PORT", 5000))

    # Запускаем Telegram бота в отдельном потоке
    Thread(target=run_bot).start()

    # Запускаем Flask сервер
    app.run(host="0.0.0.0", port=port)

