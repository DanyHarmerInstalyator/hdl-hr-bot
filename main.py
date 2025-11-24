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
    """Принудительно устанавливаем webhook при старте"""
    logger.info(f"Устанавливаем webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook успешно установлен")

def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)

    app = web.Application()

    # Регистрируем обработчик webhook
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    # Health-check
    async def health(request):
        return web.Response(text="✅ Bot is alive")
    app.router.add_get("/", health)

    # Устанавливаем webhook после запуска приложения
    async def on_startup(app):
        await set_webhook(bot)

    async def on_shutdown(app):
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Запуск сервера на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not config.WEBHOOK_URL:
        logger.critical("❌ WEBHOOK_URL не задан!")
        exit(1)
    main()