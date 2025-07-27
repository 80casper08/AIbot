import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
from dotenv import load_dotenv

# Завантажуємо .env
load_dotenv()

# Налаштування токенів
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ініціалізація ботів
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я AI бот 🤖 Напиши мені будь-що!")

@dp.message()
async def chat_gpt(message: types.Message):
    user_message = message.text

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ти дружелюбний Telegram-бот ChatGPT."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    await message.answer(reply)


if __name__ == "__main__":
    import asyncio

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
