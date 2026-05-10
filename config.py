import os
from dotenv import load_dotenv


# .env faylni o‘qib olamiz
load_dotenv()

# Bot tokenni .env ichidan olamiz
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Agar token bo‘lmasa, xato chiqaramiz
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi. .env faylga BOT_TOKEN yozing.")