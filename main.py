import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "TOKEN1"

# --- Тексти ---
INFO_TEXT = (
    "📢 Колеги, доброго дня!\n\n"
    "З серпня для розмітки підлоги на локації (5S) "
    "будемо використовувати 🟧 *помаранчеву стрічку* замість жовтої.\n\n"
    "▪ Для робочих місць тимчасово застосовуємо вузьку жовту стрічку, "
    "доки не буде використано запас.\n"
    "▪ Візуалізації у Confluence вже оновлено.\n"
    "▪ На виробництві поступово також здійснюватиметься заміна.\n\n"
    "🔸 Просимо довести інформацію до підлеглих."
)

QUIZ_QUESTIONS = [
    {
        "question": "Якого кольору тепер буде стрічка для розмітки підлоги?",
        "options": ["🟨 Жовта", "🟧 Помаранчева", "🟩 Зелена"],
        "answer": "🟧 Помаранчева"
    },
    {
        "question": "Де тимчасово залишиться жовта стрічка?",
        "options": ["На складі", "На робочих місцях", "У коридорах"],
        "answer": "На робочих місцях"
    }
]

INTERVIEW_QUESTIONS = [
    {
        "question": "Що таке 5S?",
        "options": ["Метод організації робочого місця", "Система оплати праці", "Вид обладнання"],
        "answer": "Метод організації робочого місця"
    },
    {
        "question": "Що робити, якщо план виробництва не виконується?",
        "options": ["Ігнорувати", "Зібрати команду та шукати рішення", "Покарати працівників"],
        "answer": "Зібрати команду та шукати рішення"
    },
    {
        "question": "Які ваші дії у випадку травматизму на дільниці?",
        "options": ["Надати першу допомогу і повідомити HSE", "Сховати випадок", "Відправити людину додому"],
        "answer": "Надати першу допомогу і повідомити HSE"
    },
    {
        "question": "Як ви мотивуєте підлеглих?",
        "options": ["Погрозами", "Чесним ставленням і прикладом", "Ігноруванням проблем"],
        "answer": "Чесним ставленням і прикладом"
    }
]

# --- Стан ---
user_state = {}

# --- Хендлери ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋 Я бот для навчання з 5S та підготовки до співбесіди!\n\n"
        "Використай:\n"
        "👉 /info — дізнатись про зміну розмітки\n"
        "👉 /quiz — пройти короткий тест\n"
        "👉 /interview — тренувальні питання від директора"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(INFO_TEXT, parse_mode="Markdown")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(QUIZ_QUESTIONS)
    user_state[update.effective_chat.id] = question
    keyboard = [[opt] for opt in question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(question["question"], reply_markup=markup)

async def interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(INTERVIEW_QUESTIONS)
    user_state[update.effective_chat.id] = question
    keyboard = [[opt] for opt in question["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(question["question"], reply_markup=markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_state:
        return

    question = user_state[chat_id]
    answer = update.message.text

    if answer == question["answer"]:
        await update.message.reply_text("✅ Правильно!", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(
            f"❌ Неправильно. Правильна відповідь: {question['answer']}",
            reply_markup=ReplyKeyboardRemove()
        )

    del user_state[chat_id]

# --- Запуск ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("interview", interview))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    app.run_polling()

if __name__ == "__main__":
    main()
