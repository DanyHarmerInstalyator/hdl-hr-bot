# config.py
import os


BOT_TOKEN = os.environ["BOT_TOKEN"]  # упадёт с KeyError, если не задан
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")  # убираем лишний слеш
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x]