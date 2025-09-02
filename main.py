import os
import random
from flask import Flask, request
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

# --- Імпорт питань ---
from questions import questions

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("TOKEN не задано в .env файлі!")

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://dashboard.render.com/web/srv-d2rfh2qdbo4c73d95sag/deploys/dep-d2rfh32dbo4c73d95sm0?r=2025-09-02%4013%3A59%3A46%7E2025-09-02%4014%3A03%3A20{WEBHOOK_PATH}"  # Замінити на URL Render

# --- Aiogram ---
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Стани ---
class QuizState(StatesGroup):
    question_index = State()
    selected_options = State()
    temp_selected = State()

# --- Flask ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return "OK", 200

# --- Логування ---
def log_result(user: types.User, score=None, started=False):
    with open("logs.txt", "a", encoding="utf-8") as f:
        if started:
            f.write(f"{user.full_name} | {user.id} | Розпочав тест\n")
        else:
            f.write(f"{user.full_name} | {user.id} | Завершив тест | {score}%\n")

# --- Клавіатура старту ---
def main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🚀 Почати")]],
        resize_keyboard=True
    )

# --- /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Натисни кнопку, щоб розпочати тест:",
        reply_markup=main_keyboard()
    )

# --- Почати квіз ---
@dp.message(lambda m: m.text == "🚀 Почати")
async def start_quiz(message: types.Message, state: FSMContext):
    questions_list = questions
    await state.set_state(QuizState.question_index)
    await state.update_data(
        question_index=0,
        selected_options=[],
        temp_selected=set(),
        questions=questions_list
    )
    log_result(message.from_user, started=True)
    await send_question(message, state)

# --- Відправка питання ---
async def send_question(message_or_callback, state: FSMContext):
    data = await state.get_data()
    questions_list = data["questions"]
    index = data["question_index"]

    if index >= len(questions_list):
        # Кінець тесту
        correct = 0
        for i, q in enumerate(questions_list):
            correct_answers = {j for j, (_, is_correct) in enumerate(q["options"]) if is_correct}
            user_selected = set(data["selected_options"][i])
            if correct_answers == user_selected:
                correct += 1
        percent = round(correct / len(questions_list) * 100)
        log_result(message_or_callback.from_user, percent)
        await message_or_callback.answer(
            f"📊 Тест завершено!\n✅ Правильних відповідей: {correct}/{len(questions_list)}\n📈 Успішність: {percent}%"
        )
        return

    question = questions_list[index]
    text = question["text"]
    options = list(enumerate(question["options"]))
    random.shuffle(options)
    selected = data.get("temp_selected", set())

    buttons = [[InlineKeyboardButton(
        text=("✅ " if i in selected else "◻️ ") + label,
        callback_data=f"opt_{i}"
    )] for i, (label, _) in options]
    buttons.append([InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)

# --- Обробка вибору ---
@dp.callback_query(lambda c: c.data.startswith("opt_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected.symmetric_difference_update({index})
    await state.update_data(temp_selected=selected)
    await send_question(callback, state)

@dp.callback_query(lambda c: c.data == "confirm")
async def confirm_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected_options = data.get("selected_options", [])
    selected_options.append(list(selected))
    await state.update_data(
        selected_options=selected_options,
        question_index=data["question_index"] + 1,
        temp_selected=set()
    )
    await send_question(callback, state)

# --- Старт webhook ---
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
