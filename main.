import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from questions import op_questions  # імпортуємо потрібні питання

# --- Flask для Render ---
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is running!"
Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

# --- Aiogram ---
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Стани ---
class QuizState(StatesGroup):
    question_index = State()
    selected_options = State()
    temp_selected = State()

# --- Функції ---
def main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🚀 Почати")]],
        resize_keyboard=True
    )

def log_result(user: types.User, score: int = None, started: bool = False):
    # просте логування в logs.txt
    with open("logs.txt", "a", encoding="utf-8") as f:
        if started:
            f.write(f"{user.full_name} | {user.id} | Розпочав тест\n")
        else:
            f.write(f"{user.full_name} | {user.id} | Завершив тест | {score}%\n")

# --- Старт ---
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Натисни кнопку, щоб розпочати тест:",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "🚀 Почати")
async def start_quiz(message: types.Message, state: FSMContext):
    questions = op_questions  # обираємо питання для тесту
    await state.set_state(QuizState.question_index)
    await state.update_data(question_index=0, selected_options=[], temp_selected=set(), questions=questions)
    log_result(message.from_user, started=True)
    await send_question(message, state)

async def send_question(message_or_callback, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["question_index"]

    if index >= len(questions):
        # Результат
        correct = 0
        for i, q in enumerate(questions):
            correct_answers = {j for j, (_, is_correct) in enumerate(q["options"]) if is_correct}
            user_selected = set(data["selected_options"][i])
            if correct_answers == user_selected:
                correct += 1
        percent = round(correct / len(questions) * 100)
        log_result(message_or_callback.from_user, percent)

        await message_or_callback.answer(f"📊 Тест завершено!\n✅ Правильних відповідей: {correct}/{len(questions)}\n📈 Успішність: {percent}%")
        return

    # Питання
    question = questions[index]
    text = question["text"]
    options = list(enumerate(question["options"]))
    random.shuffle(options)
    selected = data.get("temp_selected", set())

    buttons = [[InlineKeyboardButton(text=("✅ " if i in selected else "◻️ ") + label, callback_data=f"opt_{i}")] for i, (label, _) in options]
    buttons.append([InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("opt_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected.symmetric_difference_update({index})
    await state.update_data(temp_selected=selected)
    await send_question(callback, state)

@dp.callback_query(F.data == "confirm")
async def confirm_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected_options = data.get("selected_options", [])
    selected_options.append(list(selected))
    await state.update_data(selected_options=selected_options, question_index=data["question_index"] + 1, temp_selected=set())
    await send_question(callback, state)

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
