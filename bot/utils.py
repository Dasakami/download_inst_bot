import os
import instaloader
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "/app/sessions/dskenglish.dsk.session"

loader = instaloader.Instaloader()

if os.path.exists(SESSION_FILE):
    print("Загружаем существующую сессию...")
    loader.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
else:
    print("Сессия не найдена, логинимся...")
    loader.login(IG_USERNAME, IG_PASSWORD)
    loader.save_session_to_file(SESSION_FILE)

cloudinary.config(
    cloud_name='dmo1w8jv3',
    api_key='389289238549655',
    api_secret='o9x3aYhIU-5KscBekBHHeo-m28E'
)

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
