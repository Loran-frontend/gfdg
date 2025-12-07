import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# --- Настройки ---
TOKEN = "8394612560:AAEA_-8I-TMpW7LxCEmGHBu8uWa6FMoHcJk"
if not TOKEN:
    raise ValueError("Установите переменную окружения TOKEN")

PORT = int(os.environ.get("PORT", 5000))
# PUBLIC_URL нужно установить в Environment Variables Railway, например: https://your-app.up.railway.app
PUBLIC_URL = "gfdg-production.up.railway.app"
if not PUBLIC_URL:
    raise ValueError("Установите переменную окружения PUBLIC_URL с вашим Railway URL")

WEBHOOK_PATH = f"/{TOKEN}"  # защищённый путь webhook

# --- Инициализация ---
app = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

# --- Хранилища кодов ---
active_codes = {}
used_codes = {}

# --- Flask API ---
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
    application.update_queue.put(update)
    return "OK"

# --- Telegram обработчик сообщений ---
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

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# --- Запуск ---
if __name__ == "__main__":
    # Установка webhook на Telegram
    webhook_url = f"{PUBLIC_URL}{WEBHOOK_PATH}"
    bot.set_webhook(webhook_url)
    print(f"[INFO] Webhook установлен: {webhook_url}")
      # Запуск Flask сервера
    app.run(host="0.0.0.0", port=PORT)

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling()

  

