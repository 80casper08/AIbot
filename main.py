import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота з оточення
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Парсер погоди з sinoptik.ua
def get_weather_synoptik(city: str) -> str:
    city = city.strip().lower().replace(" ", "-")
    url = f"https://sinoptik.ua/погода-{city}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Не вдалося отримати дані з sinoptik.ua. Перевірте назву міста."

    soup = BeautifulSoup(response.content, "html.parser")

    try:
        city_name = soup.find("div", class_="tabs").find("h1").text.strip()
        temperature = soup.find("p", class_="today-temp").text.strip()
        description = soup.find("div", class_="description").text.strip()
        return f"{city_name}\n🌡 {temperature}\n{description}"
    except Exception as e:
        return "Не вдалося розібрати сторінку. Можливо, змінився дизайн або назва міста неправильна."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Введи назву міста українською, щоб отримати прогноз з sinoptik.ua.")

# Обробка тексту
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    weather_info = get_weather_synoptik(city)
    await update.message.reply_text(weather_info)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
