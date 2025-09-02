from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import random

from questions import QUIZ_QUESTIONS  # твій файл з питаннями

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# словник для збереження стану користувачів (яке питання показано)
user_state = {}

# функція для відправки питання
async def send_question(user_id, chat_id):
    question = random.choice(QUIZ_QUESTIONS)
    user_state[user_id] = question  # зберігаємо поточне питання
    keyboard = InlineKeyboardBuilder()
    for opt in question["options"]:
        keyboard.add(types.InlineKeyboardButton(text=opt, callback_data=opt))
    await bot.send_message(chat_id, question["question"], reply_markup=keyboard.as_markup())

# старт
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    # видаляємо попереднє повідомлення, якщо є
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass
    await send_question(message.from_user.id, message.chat.id)

# обробка натискання на варіант відповіді
@dp.callback_query()
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    answer = callback.data
    current_question = user_state.get(user_id)

    if current_question:
        if answer == current_question["answer"]:
            text = f"✅ Правильно!"
        else:
            text = f"❌ Неправильно! Правильна відповідь: {current_question['answer']}"

        # видаляємо старе питання
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)

        # надсилаємо наступне питання
        await send_question(user_id, chat_id)

        # підтвердження callback
        await callback.answer(text)
