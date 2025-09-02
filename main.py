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
from questions import questions  # Усі питання з одного файлу

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/ping")
def ping():
    return "OK", 200

Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

ADMIN_IDS = [710633503, 716119785]
GROUP_ID = -1002786428793  
PING_INTERVAL = 6 * 60 * 60 

class QuizState(StatesGroup):
    question_index = State()
    selected_options = State()
    temp_selected = State()
    current_message_id = State()
    current_options = State()


# Стартова кнопка
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🚀 Почати")]],
        resize_keyboard=True
    )
    await message.answer("Привіт! Натисни 'Почати', щоб пройти тест.", reply_markup=keyboard)


# Початок тесту
@dp.message(F.text == "🚀 Почати")
async def start_quiz(message: types.Message, state: FSMContext):
    shuffled_questions = questions.copy()
    random.shuffle(shuffled_questions)

    await state.set_state(QuizState.question_index)
    await state.update_data(
        question_index=0,
        selected_options=[],
        temp_selected=set(),
        questions=shuffled_questions
    )
    await send_question(message.chat.id, state)


async def send_question(chat_id, state: FSMContext):
    data = await state.get_data()
    index = data["question_index"]
    questions_list = data["questions"]

    if index >= len(questions_list):
        selected_all = data.get("selected_options", [])
        correct = 0
        for i, q in enumerate(questions_list):
            correct_indices = {j for j, (_, ok) in enumerate(q["options"]) if ok}
            user_selected = set(selected_all[i])
            if correct_indices == user_selected:
                correct += 1
        percent = round(correct / len(questions_list) * 100)
        await bot.send_message(chat_id, f"📊 Результат тесту: {correct} з {len(questions_list)} ({percent}%)")
        return

    question = questions_list[index]
    options = list(enumerate(question["options"]))
    random.shuffle(options)
    await state.update_data(current_options=options, temp_selected=set())

    buttons = [[InlineKeyboardButton(text="◻️ " + opt_text, callback_data=f"opt_{i}")] for i, (opt_text, _) in options]
    buttons.append([InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if "image" in question and question["image"]:
        msg = await bot.send_photo(chat_id, photo=question["image"], caption=question["text"], reply_markup=keyboard)
    else:
        msg = await bot.send_message(chat_id, text=question["text"], reply_markup=keyboard)

    await state.update_data(current_message_id=msg.message_id)


@dp.callback_query(F.data.startswith("opt_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected.symmetric_difference_update({index})
    await state.update_data(temp_selected=selected)

    options = data["current_options"]
    buttons = [[InlineKeyboardButton(text=("✅ " if i in selected else "◻️ ") + text, callback_data=f"opt_{i}")] for i, (text, _) in options]
    buttons.append([InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm")])
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=data["current_message_id"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@dp.callback_query(F.data == "confirm")
async def confirm_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("temp_selected", set())
    selected_options = data.get("selected_options", [])
    selected_options.append(list(selected))
    await state.update_data(selected_options=selected_options, question_index=data["question_index"] + 1, temp_selected=set())
    await send_question(callback.message.chat.id, state)


async def send_ping():
    while True:
        try:
            await bot.send_message(GROUP_ID, "✅ Я працююю! ✅")
        except Exception as e:
            print(f"❗ Помилка пінгу: {e}")
        await asyncio.sleep(PING_INTERVAL)


async def main():
    asyncio.create_task(send_ping())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
