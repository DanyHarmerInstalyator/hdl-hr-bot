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
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from handlers import common, onboarding, admin
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Запуск бота...")
    if config.WEBHOOK_URL:
        webhook_url = f"{config.WEBHOOK_URL}/webhook"
        logger.info(f"Установка webhook на: {webhook_url}")
        await bot.set_webhook(webhook_url)
        logger.info("Webhook успешно установлен")
    else:
        logger.warning("WEBHOOK_URL не задан — бот не будет получать обновления на Render!")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    if config.WEBHOOK_URL:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален")

def main():
    # Инициализация
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)

    # Регистрируем события
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Создаём aiohttp приложение
    app = web.Application()

    # Регистрируем Aiogram-приложение в aiohttp (автоматически добавляет /webhook)
    setup_application(app, dp, bot=bot)

    # Health-check для Render
    async def health_check(request):
        return web.Response(text="✅ Bot is running on Render")

    app.router.add_get("/", health_check)

    # Получаем порт от Render
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Запуск webhook-сервера на 0.0.0.0:{port}")

    # Запуск
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    logger.info("Инициализация бота...")
    if not config.WEBHOOK_URL:
        logger.critical("Ошибка: WEBHOOK_URL не задан. На Render бот работает ТОЛЬКО в webhook-режиме.")
        exit(1)
    main()