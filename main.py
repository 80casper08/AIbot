import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuizStates(StatesGroup):
    choosing_section = State()
    asking_question = State()
    showing_result = State()

DATA_PATH = Path("data/questions_example.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    questions_data = json.load(f)

def main_menu_kb():
    kb = ReplyKeyboardBuilder()
    for sec in questions_data.keys():
        kb.button(text=sec)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def repeat_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔄 Пройти ще раз")
    kb.button(text="🏠 Головне меню")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вітаю! Оберіть розділ ПДР для проходження тесту:", reply_markup=main_menu_kb())
    await state.set_state(QuizStates.choosing_section)

@dp.message(QuizStates.choosing_section)
async def choose_section(message: types.Message, state: FSMContext):
    chosen = message.text
    if chosen not in questions_data:
        await message.answer("Будь ласка, оберіть розділ із кнопок.")
        return
    await state.update_data(chosen_section=chosen, question_index=0, score=0)
    await message.answer(f"Обрали розділ {chosen}. Починаємо тест!", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(QuizStates.asking_question)
    await ask_question(message, state)

async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    section = data.get("chosen_section")
    q_index = data.get("question_index", 0)
    questions = questions_data.get(section, [])

    if q_index >= len(questions):
        score = data.get("score", 0)
        await message.answer(f"Тест завершено! Ваш результат: {score} балів.", reply_markup=repeat_kb())
        await state.set_state(QuizStates.showing_result)
        return

    q = questions[q_index]
    kb = ReplyKeyboardBuilder()
    for option in q["options"]:
        kb.button(text=option)
    kb.adjust(1)
    await message.answer(f"Питання {q_index +1}:\n{q['question']}", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message(QuizStates.asking_question)
async def answer_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    section = data.get("chosen_section")
    q_index = data.get("question_index", 0)
    questions = questions_data.get(section, [])

    if q_index >= len(questions):
        await message.answer("Нема питань у цьому розділі.")
        return

    q = questions[q_index]
    answer_text = message.text

    if answer_text == q["options"][q["correct"]]:
        score = data.get("score", 0) + 1
        await state.update_data(score=score)

    await state.update_data(question_index=q_index + 1)
    await ask_question(message, state)

@dp.message(QuizStates.showing_result)
async def after_result(message: types.Message, state: FSMContext):
    if message.text == "🔄 Пройти ще раз":
        data = await state.get_data()
        section = data.get("chosen_section")
        await state.update_data(question_index=0, score=0)
        await message.answer(f"Повторюємо тест з розділу {section}. Починаємо!", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(QuizStates.asking_question)
        await ask_question(message, state)
    elif message.text == "🏠 Головне меню":
        await state.clear()
        await message.answer("Обери розділ:", reply_markup=main_menu_kb())
        await state.set_state(QuizStates.choosing_section)
    else:
        await message.answer("Виберіть кнопку.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
