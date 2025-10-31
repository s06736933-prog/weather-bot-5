import os
import requests
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Инициализация бота
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Создаем клавиатуру с кнопкой
weather_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌤 Узнать погоду в Старой Руссе")]
    ],
    resize_keyboard=True
)

# Функция для получения погоды
async def get_weather(city: str) -> str:
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return "❌ API ключ для погоды не настроен"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            
            return (f"🌤 Погода в Старой Руссе:\n"
                    f"• Температура: {temp:.1f}°C\n"
                    f"• Ощущается как: {feels_like:.1f}°C\n"
                    f"• Влажность: {humidity}%\n"
                    f"• {description.capitalize()}\n"
                    f"• Ветер: {wind_speed} м/с")
        else:
            return "❌ Не удалось получить данные о погоде"
            
    except Exception as e:
        logger.error(f"Ошибка получения погоды: {e}")
        return f"❌ Ошибка при получении погоды: {str(e)}"

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот, который подскажет текущую погоду в Старой Руссе.",
        reply_markup=weather_kb
    )

# Обработчик кнопки и текстовых запросов
@dp.message()
async def handle_weather_request(message: Message):
    text = message.text.lower()
    
    if "погод" in text and "старой руссе" in text or text == "🌤 узнать погоду в старой руссе":
        weather_info = await get_weather("Staraya Russa")
        await message.answer(weather_info, reply_markup=weather_kb)
    elif "погод" in text:
        await message.answer("Нажмите кнопку ниже для получения погоды", reply_markup=weather_kb)
    else:
        await message.answer("Используйте кнопки для взаимодействия с ботом", reply_markup=weather_kb)

# Фиктивный HTTP-сервер для Render
async def handle(request):
    return web.Response(text="Bot is running")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print("✅ Фиктивный сервер запущен на порту 8000")

# Запуск бота
async def main():
    logger.info("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем фиктивный сервер и бота
    loop = asyncio.get_event_loop()
    loop.create_task(start_dummy_server())
    loop.run_until_complete(main())