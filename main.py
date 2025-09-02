import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Text
from aiogram.utils import executor

TOKEN = "ТВОЙ_ТОКЕН_ТУТ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

SP_QUESTIONS = [
    {
        "question": "Хто має повідомити HR Lead локації про прогул працівника?",
        "options": ["Безпосередній керівник", "Head of Department", "HR Documentation Specialist"],
        "answer": "Безпосередній керівник"
    },
    {
        "question": "Який документ складає керівник, якщо працівник не вийшов на роботу і відмовляється писати пояснювальну?",
        "options": ["Акт відмови надати пояснення", "Доповідна записка", "Табель"],
        "answer": "Акт відмови надати пояснення"
    },
    # ... додати інші питання ...
]

user_data = {}

def get_markup(options):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    return markup

@dp.message(commands=["start"])
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    questions = SP_QUESTIONS.copy()
    random.shuffle(questions)
    user_data[user_id] = {"questions": questions, "current": 0, "message_id": None}

    msg = await message.answer(questions[0]["question"], reply_markup=get_markup(questions[0]["options"]))
    user_data[user_id]["message_id"] = msg.message_id

@dp.message()
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Натисніть /start для початку опитування")
        return

    current_index = user_data[user_id]["current"]
    question = user_data[user_id]["questions"][current_index]

    if message.text == question["answer"]:
        await message.answer("✅ Правильно!")
    else:
        await message.answer(f"❌ Неправильно! Правильна відповідь: {question['answer']}")

    next_index = current_index + 1
    if next_index < len(user_data[user_id]["questions"]):
        msg = await message.answer(
            user_data[user_id]["questions"][next_index]["question"],
            reply_markup=get_markup(user_data[user_id]["questions"][next_index]["options"])
        )
        user_data[user_id]["current"] = next_index
        user_data[user_id]["message_id"] = msg.message_id
    else:
        await message.answer("🎉 Ви пройшли всі питання!", reply_markup=types.ReplyKeyboardRemove())
        user_data.pop(user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
