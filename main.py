import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Завантаження питань з GitHub ---
GITHUB_URL = "https://raw.githubusercontent.com/твій_юзер/твій_репо/main/questions.py"

resp = requests.get(GITHUB_URL)
if resp.status_code == 200:
    exec(resp.text)  # тепер у нас буде змінна questions із файлу
else:
    raise Exception("Не вдалося завантажити questions.py з GitHub")

# --- Поточний стан ---
user_data = {}

# --- Старт ---
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🚀 Почати")]],
        resize_keyboard=True
    )
    await message.answer("Привіт! Натисни кнопку, щоб почати тест:", reply_markup=keyboard)

@dp.message(F.text == "🚀 Почати")
async def start_quiz(message: types.Message):
    user_data[message.from_user.id] = {
        "question_index": 0,
        "selected_options": [],
        "temp_selected": set()
    }
    await send_question(message.from_user.id, message)

# --- Показати питання ---
async def send_question(user_id, message_or_callback):
    data = user_data[user_id]
    index = data["question_index"]

    if index >= len(questions):
        # Результат
        correct = 0
        for i, q in enumerate(questions):
            correct_answers = {j for j, (_, is_correct) in enumerate(q["options"]) if is_correct}
            user_selected = set(data["selected_options"][i])
            if correct_answers == user_selected:
                correct += 1
        await message_or_callback.answer(f"📊 Тест завершено!\n✅ Правильних відповідей: {correct}/{len(questions)}")
        del user_data[user_id]
        return

    # Питання
    q = questions[index]
    opts = list(enumerate(q["options"]))
    random.shuffle(opts)
    selected = data.get("temp_selected", set())
    buttons = [[InlineKeyboardButton(text=("✅ " if i in selected else "◻️ ") + label, callback_data=f"opt_{i}")] for i, (label, _) in opts]
    buttons.append([InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(q["text"], reply_markup=keyboard)
    else:
        await message_or_callback.answer(q["text"], reply_markup=keyboard)

# --- Обробка вибору ---
@dp.callback_query(F.data.startswith("opt_"))
async def toggle_option(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[1])
    data = user_data[user_id]
    selected = data.get("temp_selected", set())
    selected.symmetric_difference_update({index})
    data["temp_selected"] = selected
    await send_question(user_id, callback)

@dp.callback_query(F.data == "confirm")
async def confirm_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data[user_id]
    selected = data.get("temp_selected", set())
    data["selected_options"].append(list(selected))
    data["question_index"] += 1
    data["temp_selected"] = set()
    await send_question(user_id, callback)

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
