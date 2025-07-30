import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def get_synoptyk_weather(city):
    city_url = city.lower().replace(" ", "-")
    url = f"https://sinoptik.ua/погода-{city_url}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "⚠️ Не вдалося отримати дані. Перевірте назву міста."

    soup = BeautifulSoup(response.content, "html.parser")
    try:
        temp_now = soup.find("p", class_="today-temp").text.strip()
        description = soup.find("div", class_="description").find("div").text.strip()
        return f"🌤 Погода в {city.title()}:\n{description}\n🌡 Температура: {temp_now}"
    except Exception as e:
        logging.error(e)
        return "⚠️ Не вдалося розпарсити сторінку. Можливо змінився HTML."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот з погодою (Synoptyk.ua).\nНапишіть /weather <місто>"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Вкажіть місто. Наприклад: /weather Київ")
    else:
        city = " ".join(context.args)
        weather_info = get_synoptyk_weather(city)
        await update.message.reply_text(weather_info)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    print("Бот запущено...")
    app.run_polling()
