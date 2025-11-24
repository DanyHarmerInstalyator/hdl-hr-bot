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
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from handlers import common, onboarding, admin
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{config.WEBHOOK_URL}{WEBHOOK_PATH}"

async def on_bot_startup(bot: Bot):
    logger.info(f"Установка webhook на {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook установлен")

async def on_bot_shutdown(bot: Bot):
    logger.info("Удаление webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook удалён")

def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)

    # Явно регистрируем startup/shutdown с ботом
    dp.startup.register(lambda: on_bot_startup(bot))
    dp.shutdown.register(lambda: on_bot_shutdown(bot))

    app = web.Application()

    # Регистрируем webhook-обработчик
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    # Health-check
    async def health_check(request):
        return web.Response(text="✅ Bot is running")

    app.router.add_get("/", health_check)

    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Сервер запущен на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not config.WEBHOOK_URL:
        logger.critical("❌ WEBHOOK_URL не задан!")
        exit(1)
    main()