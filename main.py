import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import common, onboarding, admin
from database import db  # Импортируем глобальный экземпляр db
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Запуск бота...")
    if config.WEBHOOK_URL:
        await bot.set_webhook(f"{config.WEBHOOK_URL}/webhook")
        logger.info(f"Webhook установлен: {config.WEBHOOK_URL}/webhook")
    else:
        logger.warning("WEBHOOK_URL не установлен, бот будет работать в polling режиме")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    if config.WEBHOOK_URL:
        await bot.delete_webhook()
        logger.info("Webhook удален")

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
    # База данных уже инициализирована при создании экземпляра Database()
    logger.info("База данных инициализирована")
    
    # Получение порта из переменных окружения
    port = int(os.environ.get("PORT", 10000))
    
    # Запуск приложения
    app = create_app()
    
    logger.info(f"Бот запущен в режиме webhook на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)