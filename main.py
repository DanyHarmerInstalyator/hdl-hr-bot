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
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import common, onboarding, admin
from database import db

# Включаем логирование
logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Запуск бота...")
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(common.router)
    dp.include_router(onboarding.router)
    dp.include_router(admin.router)  # Добавляем админ-панель
    
    # Инициализируем базу данных
    db.init_db()
    logging.info("База данных инициализирована")

    logging.info("Бот запущен и ожидает сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())