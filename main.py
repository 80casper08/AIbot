# main.py
import os
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from questions import QUIZ_QUESTIONS, INTERVIEW_QUESTIONS

TOKEN = os.getenv("TOKEN")  # Твій токен бота у змінних середовища

user_state = {}  # тут зберігатимемо поточне питання для кожного користувача

# --- Хендлери ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відправляє привітальне повідомлення та одразу рандомне питання"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "Привіт 👋 Я бот для навчання з 5S та підготовки до співбесіди!\n\n"
        "Одразу почнемо з питання:"
    )
    await send_random_question(chat_id, update, context)


async def send_random_question(chat_id, update, context, quiz=True):
    """Відправляє рандомне питання з QUIZ або INTERVIEW"""
    questions_list = QUIZ_QUESTIONS if quiz else INTERVIEW_QUESTIONS
    question = random.choice(questions_list)
    user_state[chat_id] = question

    keyboard = [[opt] for opt in question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    # Відправляємо нове питання і зберігаємо повідомлення
    msg = await update.message.reply_text(question["question"], reply_markup=markup)
    user_state[chat_id]["message_id"] = msg.message_id


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє відповідь користувача"""
    chat_id = update.effective_chat.id
    if chat_id not in user_state:
        return

    question = user_state[chat_id]
    answer = update.message.text

    # Видаляємо попереднє питання
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=question["message_id"])
    except:
        pass  # Якщо повідомлення вже видалено або немає прав, ігноруємо

    # Відправляємо результат
    if answer == question["answer"]:
        await update.message.reply_text("✅ Правильно!", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(f"❌ Неправильно. Правильна відповідь: {question['answer']}", reply_markup=ReplyKeyboardRemove())

    # Відправляємо наступне питання
    await send_random_question(chat_id, update, context)


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /quiz"""
    await send_random_question(update.effective_chat.id, update, context, quiz=True)

async def interview_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /interview"""
    await send_random_question(update.effective_chat.id, update, context, quiz=False)


if __name__ == "__main__":
    # Створюємо Application
    application = Application.builder().token(TOKEN).build()

    # Додаємо хендлери
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("interview", interview_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Запускаємо бот
    application.run_polling()
