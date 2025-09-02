import os
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from questions import questions

TOKEN = os.getenv("TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://aibot-mgod.onrender.com{WEBHOOK_PATH}"  # твій URL Render

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

app = Flask(__name__)

# --- Стартова клавіатура ---
def main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🚀 Почати")]],
        resize_keyboard=True
    )

# --- Команди ---
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Натисни кнопку, щоб розпочати тест:", reply_markup=main_keyboard())

# --- Приклад обробки кнопки ---
@dp.message(lambda message: message.text == "🚀 Почати")
async def start_quiz(message: types.Message):
    await message.answer("Тут почнеться тест...")  # встав сюди свою логіку

# --- Flask webhook ---
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = types.Update(**await request.get_json())
    await dp.process_update(update)
    return "OK"

# --- Налаштування webhook при старті ---
async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
