import os
import instaloader
import psycopg2
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Загрузка .env
load_dotenv()

# Telegram токен
TOKEN = os.getenv("TOKEN") or '7273476577:AAFxXgDEtEAlu5tHUPWqcTUHAvoleTEeeKA'

# Cloudinary config
cloudinary.config(
    cloud_name='dmo1w8jv3',
    api_key='389289238549655',
    api_secret='o9x3aYhIU-5KscBekBHHeo-m28E'
)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключение к БД (если нужно)
conn = psycopg2.connect(
    dbname='insta_bot_db',
    user='postgres',
    password='1908',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()


# Функция загрузки видео в Cloudinary
def upload_to_cloudinary(file_path):
    try:
        result = cloudinary.uploader.upload_large(file_path, resource_type="video")
        return result.get("secure_url")
    except Exception as e:
        print(f"Ошибка при загрузке в Cloudinary: {e}")
        return None


# Скачивание видео из Instagram
def download_instagram_video(url):
    loader = instaloader.Instaloader()
    try:
        post_shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        video_url = post.video_url
        if video_url:
            response = requests.get(video_url)
            if response.status_code == 200:
                os.makedirs("videos", exist_ok=True)
                file_name = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
                file_path = os.path.join("videos", file_name)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return file_path
        raise Exception("Видео не найдено.")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("👋 Привет! Отправь мне ссылку на видео из Instagram, и я скачаю его для тебя!")


# Обработка сообщений
@dp.message()
async def handle_message(message: Message):
    insta_url = message.text.strip()

    if "instagram.com" not in insta_url:
        await message.answer("🚫 Пожалуйста, отправь корректную ссылку на видео из Instagram.")
        return

    await message.answer("⏳ Скачиваю видео...")

    video_path = download_instagram_video(insta_url)

    if video_path:
        await message.answer("☁️ Загружаю в облако...")

        cloud_url = upload_to_cloudinary(video_path)

        if cloud_url:
            await message.answer_video(cloud_url, caption="✅ Вот твоё видео из Instagram!")
        else:
            await message.answer("⚠️ Не удалось загрузить видео в облако.")
        
        # Удаляем локальный файл
        os.remove(video_path)
    else:
        await message.answer("❌ Не удалось скачать видео. Попробуй другую ссылку.")


# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
