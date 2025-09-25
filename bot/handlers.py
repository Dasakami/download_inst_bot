from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from .states import user_state
from .utils import download_instagram_video, download_instagram_photo, upload_to_cloudinary
import os 
async def register_handlers(dp):

    @dp.message(Command("start"))
    async def start_command(message: types.Message):
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
    async def handle_message(message: types.Message):
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
