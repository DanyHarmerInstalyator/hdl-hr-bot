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
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import common, onboarding, admin
from database import init_db
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Запуск бота...")
    await bot.set_webhook(f"{config.WEBHOOK_URL}/webhook")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    await bot.delete_webhook()

def create_app():
    """Создание aiohttp приложения"""
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)
    
    # События запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Создание aiohttp приложения
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Регистрация webhook пути
    webhook_requests_handler.register(app, path="/webhook")
    
    # Health check endpoint
    async def health_check(request):
        return web.Response(text="Bot is running")
    
    app.router.add_get("/", health_check)
    
    return app

if __name__ == "__main__":
    # Инициализация базы данных
    init_db()
    logger.info("База данных инициализирована")
    
    # Получение порта из переменных окружения (Render автоматически устанавливает)
    port = int(os.environ.get("PORT", 10000))
    
    # Запуск приложения
    app = create_app()
    
    logger.info(f"Бот запущен в режиме webhook на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)