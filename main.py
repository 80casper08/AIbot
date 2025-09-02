import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from questions import QUIZ_QUESTIONS, INTERVIEW_QUESTIONS

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не заданий у змінних середовища")

user_state = {}

def get_random_question():
    return random.choice(QUIZ_QUESTIONS + INTERVIEW_QUESTIONS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋 Я бот для навчання з 5S та підготовки до співбесіди!\n"
        "Нижче одне випадкове питання для тренування:"
    )
    question = get_random_question()
    user_state[update.effective_chat.id] = question
    keyboard = [[opt] for opt in question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)  # клавіатура постійна
    await update.message.reply_text(question["question"], reply_markup=markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_state:
        return

    question = user_state[chat_id]
    answer = update.message.text

    if answer == question["answer"]:
        await update.message.reply_text("✅ Правильно!")
    else:
        await update.message.reply_text(f"❌ Неправильно. Правильна відповідь: {question['answer']}")

    # Наступне питання
    next_question = get_random_question()
    user_state[chat_id] = next_question
    keyboard = [[opt] for opt in next_question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(next_question["question"], reply_markup=markup)

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("Bot is running...")
    application.run_polling()
