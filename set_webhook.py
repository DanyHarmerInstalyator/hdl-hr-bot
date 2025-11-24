# set_webhook.py
import asyncio
import os
from aiogram import Bot

async def main():
    bot = Bot(token="8397012285:AAFgx6-TxxgDp5HJntg_484auF5fH370IEo")
    webhook_url = "https://hdl-hr-bot-af4x.onrender.com/webhook"
    
    print("1. Удаляем старый вебхук...")
    await bot.delete_webhook()
    
    print("2. Проверяем текущий вебхук...")
    webhook_info = await bot.get_webhook_info()
    print(f"   Текущий вебхук: {webhook_info.url}")
    
    print("3. Устанавливаем новый вебхук...")
    result = await bot.set_webhook(webhook_url)
    print(f"   Результат: {result}")
    
    print("4. Проверяем установку...")
    webhook_info = await bot.get_webhook_info()
    print(f"   Новый вебхук: {webhook_info.url}")
    print(f"   Pending updates: {webhook_info.pending_update_count}")
    
    await bot.session.close()
    print("✅ Готово!")

if __name__ == "__main__":
    asyncio.run(main())