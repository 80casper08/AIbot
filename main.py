import os
import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from questions import QUIZ_QUESTIONS, INTERVIEW_QUESTIONS

TOKEN = os.getenv("TOKEN")  # або встав свій токен прямо сюди

user_state = {}  # стан користувачів

# --- Хендлери ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # Вибираємо випадкове питання з QUIZ
    question = random.choice(QUIZ_QUESTIONS + INTERVIEW_QUESTIONS)
    user_state[chat_id] = question

    # Створюємо кнопки для варіантів
    keyboard = [[opt] for opt in question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Відправляємо питання
    await update.message.reply_text(question["question"], reply_markup=markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_state:
        return

    question = user_state[chat_id]
    answer = update.message.text

    # Видаляємо попереднє питання
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id-1)
    except:
        pass  # якщо видаляти не вдається, пропускаємо

    # Відповідь
    if answer == question["answer"]:
        await update.message.reply_text("✅ Правильно!", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(f"❌ Неправильно. Правильна відповідь: {question['answer']}", reply_markup=ReplyKeyboardRemove())

    # Ставимо наступне питання
    next_question = random.choice(QUIZ_QUESTIONS + INTERVIEW_QUESTIONS)
    user_state[chat_id] = next_question
    keyboard = [[opt] for opt in next_question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(next_question["question"], reply_markup=markup)

# --- Основна функція ---
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
