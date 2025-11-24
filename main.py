# HDL HR Bot/
# ├── __pycache                     
# ├── .venv
# ├── data
# ├── documents 
# ├── handlers/  
#  └── __pycache__              
# │   └── __init__.py
# │   └── admin.py   
# │   └── common.py              
# │   └── onboarding.py  
# ├── keyboards/ 
#  └── __pycache__                  
# │   └── __init__.py
# │   └── reply.py               
# │   └── inline.py 
# ├── utils/                     
# │   └── __init__.py
# │   └── bitrix.py
# ├── videos/                     
# │   └──Hello.mp4
#  ── .env 
#  ── config_tasks.py
#  ── config.py
#  ── database.py                                        
#  ── main.py 
# ── requirements.txt                   
# ── storage.py                                 
# ── users.db


# main.py
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from handlers import common, onboarding, admin
import config

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Инициализация
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Роутеры
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)

    # Создаём aiohttp приложение
    app = web.Application()

    # 🔥 setup_application автоматически:
    # - регистрирует /webhook
    # - устанавливает webhook при старте
    # - удаляет при завершении
    webhook_path = "/webhook"
    webhook_url = f"{config.WEBHOOK_URL}{webhook_path}"

    setup_application(
        app,
        dp,
        bot=bot,
        webhook_url=webhook_url,      # ← Aiogram сам вызовет set_webhook
        webhook_path=webhook_path,    # ← маршрут, по которому слушать
    )

    # Health-check
    async def health_check(request):
        return web.Response(text="✅ Bot is running on Render")

    app.router.add_get("/", health_check)

    # Запуск
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Запуск сервера на порту {port}")
    logger.info(f"Webhook URL: {webhook_url}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not config.WEBHOOK_URL:
        logger.critical("Ошибка: WEBHOOK_URL не задан в переменных окружения!")
        exit(1)
    main()