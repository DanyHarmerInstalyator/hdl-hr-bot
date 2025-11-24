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
# main.py
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from handlers import common, onboarding, admin
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{config.WEBHOOK_URL}{WEBHOOK_PATH}"

async def set_webhook(bot: Bot):
    """Установка вебхука с обработкой ошибок"""
    try:
        # Сначала удаляем старый вебхук
        await bot.delete_webhook()
        logger.info("✅ Старый вебхук удален")
        
        # Устанавливаем новый
        result = await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}, результат: {result}")
        
        # Проверяем установку
        webhook_info = await bot.get_webhook_info()
        logger.info(f"✅ Подтверждение: вебхук установлен на {webhook_info.url}")
        logger.info(f"✅ Pending updates: {webhook_info.pending_update_count}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка установки вебхука: {e}")

def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)

    app = web.Application()

    # Регистрируем обработчик webhook
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Health-check
    async def health(request):
        return web.Response(text="✅ Bot is alive")
    
    async def webhook_info(request):
        webhook_info = await bot.get_webhook_info()
        info_text = f"""
        Webhook URL: {webhook_info.url}
        Pending updates: {webhook_info.pending_update_count}
        Has custom certificate: {webhook_info.has_custom_certificate}
        """
        return web.Response(text=info_text)

    app.router.add_get("/", health)
    app.router.add_get("/webhook-info", webhook_info)

    async def on_startup(app):
        await set_webhook(bot)

    async def on_shutdown(app):
        await bot.delete_webhook()
        await bot.session.close()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Запуск сервера на порту {port}")
    logger.info(f"WEBHOOK_URL из config: {config.WEBHOOK_URL}")
    logger.info(f"Полный URL вебхука: {WEBHOOK_URL}")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not config.WEBHOOK_URL:
        logger.critical("❌ WEBHOOK_URL не задан!")
        exit(1)
    main()