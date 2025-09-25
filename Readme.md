
---

# Instagram Downloader Bot

**Instagram Downloader Bot** — Telegram-бот для скачивания фото и видео из Instagram и загрузки их в облако (Cloudinary).

---

## 📂 Структура проекта

```
tg-instaloader-bot/
│
├─ bot/
│   ├─ __init__.py
│   ├─ main.py        # Запуск бота
│   ├─ handlers.py    # Все хэндлеры
│   ├─ states.py      # Состояния пользователей
│   └─ utils.py       # Скачивание и загрузка в облако
│
├─ sessions/          # Сессии Instagram
│   └─ *.dsk.session
├─ videos/            # Скачанные видео
├─ photos/            # Скачанные фото
├─ .env               # Секреты и токены
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

---

## ⚙️ Настройка `.env`

Скопируйте `.env.example` в `.env` и заполните:

```env
# PostgreSQL (если нужно, иначе можно убрать)
DB_USER=postgres
DB_PASS=1908
DB_NAME=botInstaBb
DB_HOST=db

# Telegram Bot
TOKEN=Ваш_токен_бота

# Instagram (Telethon для скачивания)
IG_USERNAME=Ваш_логин
IG_PASSWORD=Ваш_пароль
SESSION=/app/sessions/dskenglish.dsk.session

# Cloudinary
CLOUD_NAME=Ваш_cloud_name
CLOUD_KEY=Ваш_api_key
CLOUD_SECRET=Ваш_api_secret
```

> ⚠️ Добавьте `.env` в `.gitignore`, чтобы не публиковать токены.

---

## 🐳 Запуск через Docker

Сборка и запуск бота:

```bash
docker-compose up -d --build
```

Проверка логов:

```bash
docker-compose logs -f bot
```

Остановка:

```bash
docker-compose down
```

---

## 🐍 Локальный запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запуск бота:

```bash
python bot/main.py
```

---

## 🚀 Использование

1. Отправьте команду `/start` боту.
2. Выберите платформу `Instagram`.
3. Выберите скачивание **Фото** или **Видео**.
4. Отправьте ссылку на пост.
5. Получите файл в облаке и ссылку для скачивания.

---

## 🧪 Тестирование

```python
def test_bot_initialization():
    from bot.main import bot
    assert bot is not None
```

---

