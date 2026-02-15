import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Берем токен из настроек хостинга, а не из кода!
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🚀 СВЯЗЬ ЧЕРЕЗ GITHUB УСТАНОВЛЕНА!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())