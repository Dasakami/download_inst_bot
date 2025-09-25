import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from .handlers import register_handlers

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
