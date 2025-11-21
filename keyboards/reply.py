# keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_menu(stage: int = 1) -> ReplyKeyboardMarkup:
    keyboard = []
    

    keyboard.append([KeyboardButton(text="📂 Выбрать этап")])
    keyboard.append([KeyboardButton(text="✅ Проверить текущий этап")])  
    keyboard.append([KeyboardButton(text="📊 Мой прогресс")])
    keyboard.append([KeyboardButton(text="❓ Задать вопрос HR-менеджеру")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)