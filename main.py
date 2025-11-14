# hr_onboarding_bot/
# ├── .venv/                     # виртуальное окружение (уже создано)
# ├── .env                       # файл с секретами (токен бота)
# ├── main.py                    # точка входа
# ├── config.py                  # настройки (загрузка токена и т.п.)
# ├── keyboards/                 # клавиатуры
# │   └── __init__.py
# │   └── reply.py               # reply-клавиатуры
# │   └── inline.py              # inline-клавиатуры
# ├── handlers/                  # обработчики команд и сообщений
# │   └── __init__.py
# │   └── common.py              # базовые команды (start и т.д.)
# │   └── onboarding.py          # этапы адаптации (в т.ч. "Ввод в должность")
# ├── documents/                 # Word-документы для этапов
# │   └── stage1_intro.docx      # пример документа для этапа 1
# ├── utils/                     # вспомогательные функции (позже — интеграция с Bitrix24)
# │   └── __init__.py
# └── requirements.txt           # зависимости


# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import common, onboarding

# Включаем логирование
logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Запуск бота...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(onboarding.router) 

    logging.info("Бот запущен и ожидает сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())