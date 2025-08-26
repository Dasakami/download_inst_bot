import os
import instaloader
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

# === Telegram ===
TOKEN = os.getenv("TOKEN") or '7205482794:AAGGKupSvfeetT_CUxbX6Xe7OYLzESgxiIo'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Cloudinary ===
cloudinary.config(
    cloud_name='dmo1w8jv3',
    api_key='389289238549655',
    api_secret='o9x3aYhIU-5KscBekBHHeo-m28E'
)

# === Instagram ===
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

loader = instaloader.Instaloader()

# Сессии будут храниться в папке /app/sessions (см. Docker volume)
SESSION_DIR = "/app/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
SESSION_FILE = os.path.join(SESSION_DIR, f"{IG_USERNAME}.session")

try:
    loader.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print(f"Сессия загружена из {SESSION_FILE}")
except FileNotFoundError:
    print("Сессия не найдена, логинимся...")
    loader.login(IG_USERNAME, IG_PASSWORD)
    loader.save_session_to_file(SESSION_FILE)
    print(f"Сессия сохранена в {SESSION_FILE}")


# === Состояние пользователя ===
user_state = {}

# === Функции ===
def upload_to_cloudinary(file_path, resource_type="video"):
    try:
        result = cloudinary.uploader.upload_large(file_path, resource_type=resource_type)
        return result.get("secure_url")
    except Exception as e:
        print(f"Ошибка при загрузке в Cloudinary: {e}")
        return None

def download_instagram_video(url):
    try:
        post_shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        if not post.is_video:
            raise Exception("Это не видео.")

        video_url = post.video_url
        if not video_url:
            raise Exception("Видео не найдено.")

        os.makedirs("videos", exist_ok=True)
        file_name = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        file_path = os.path.join("videos", file_name)

        with requests.get(video_url, stream=True) as response:
            if response.status_code != 200:
                raise Exception("Не удалось скачать видео по прямой ссылке.")
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

        return file_path

    except Exception as e:
        print(f"Ошибка загрузки видео: {e}")
        return None

def download_instagram_photo(url):
    try:
        post_shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        if post.is_video:
            raise Exception("Это видео, а не фото.")

        photo_url = post.url
        response = requests.get(photo_url)
        if response.status_code != 200:
            raise Exception("Не удалось скачать фото.")

        os.makedirs("photos", exist_ok=True)
        file_name = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        file_path = os.path.join("photos", file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return file_path

    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        return None

# === Хэндлеры ===
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Instagram", callback_data="platform_instagram")],
    ])
    await message.answer("Выберите платформу для скачивания:", reply_markup=keyboard)

@dp.callback_query(F.data == "platform_instagram")
async def choose_instagram_type(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото", callback_data="insta_photo")],
        [InlineKeyboardButton(text="🎥 Видео", callback_data="insta_video")]
    ])
    await callback.message.edit_text("Что вы хотите скачать из Instagram?", reply_markup=keyboard)

@dp.callback_query(F.data == "insta_video")
async def request_insta_video_link(callback: types.CallbackQuery):
    user_state[callback.from_user.id] = "awaiting_insta_video_link"
    await callback.message.edit_text("Пожалуйста, отправьте ссылку на видео из Instagram.")

@dp.callback_query(F.data == "insta_photo")
async def request_insta_photo_link(callback: types.CallbackQuery):
    user_state[callback.from_user.id] = "awaiting_insta_photo_link"
    await callback.message.edit_text("Пожалуйста, отправьте ссылку на фото из Instagram.")

@dp.message()
async def handle_message(message: Message):
    state = user_state.get(message.from_user.id)

    if state == "awaiting_insta_video_link":
        url = message.text.strip()
        if "instagram.com" not in url:
            await message.answer("🚫 Это не похоже на ссылку Instagram. Попробуйте ещё раз.")
            return

        await message.answer("⏳ Скачиваю видео...")
        video_path = download_instagram_video(url)

        if video_path:
            await message.answer("☁️ Загружаю в облако...")
            cloud_url = upload_to_cloudinary(video_path)

            if cloud_url:
                await message.answer_video(FSInputFile(video_path), caption="✅ Вот ваше видео из Instagram!")
            else:
                await message.answer("⚠️ Не удалось загрузить видео в облако.")

            os.remove(video_path)
        else:
            await message.answer("❌ Не удалось скачать видео. Возможно, это не видео или приватный аккаунт.")

        user_state.pop(message.from_user.id, None)

    elif state == "awaiting_insta_photo_link":
        url = message.text.strip()
        if "instagram.com" not in url:
            await message.answer("🚫 Это не похоже на ссылку Instagram. Попробуйте ещё раз.")
            return

        await message.answer("⏳ Скачиваю фото...")
        photo_path = download_instagram_photo(url)

        if photo_path:
            await message.answer("☁️ Загружаю в облако...")
            cloud_url = upload_to_cloudinary(photo_path, resource_type="image")

            if cloud_url:
                await message.answer_photo(cloud_url, caption="✅ Вот ваше фото из Instagram!")
            else:
                await message.answer("⚠️ Не удалось загрузить фото в облако.")

            os.remove(photo_path)
        else:
            await message.answer("❌ Не удалось скачать фото. Возможно, это не фото или приватный аккаунт.")

        user_state.pop(message.from_user.id, None)

    else:
        await message.answer("👋 Используйте /start для начала работы с ботом.")

# === Запуск бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
