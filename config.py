# config.py
import os

BOT_TOKEN = os.environ["BOT_TOKEN"] 
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/") 
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x]

# Добавьте проверку для отладки
if not WEBHOOK_URL:
    print("❌ ВНИМАНИЕ: WEBHOOK_URL не задан!")