from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from flask import Flask, request
import threading
import openai
import os

# Токени
TELEGRAM_TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Конфігурація webhook
WEBHOOK_HOST = 'https://твій-домен.onrender.com'
WEBHOOK_PATH = f'/webhook/{TELEGRAM_TOKEN}'
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 3000))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# ✨ Flask app для пінгу
flask_app = Flask(__name__)

@flask_app.route('/')
def ping():
    return "I'm alive! 🟢", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

@dp.message_handler()
async def handle_message(message: Message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.text}]
    )
    await message.reply(response['choices'][0]['message']['content'])

async def on_startup(_):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(_):
    await bot.delete_webhook()

if __name__ == '__main__':
    # 🔁 Запускаємо Flask у окремому потоці
    threading.Thread(target=run_flask).start()

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
