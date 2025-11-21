# keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_continue_inline_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-кнопка Продолжить под видео"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Продолжить", callback_data="continue_onboarding")]
        ]
    )

def get_stage_inline_keyboard(max_stage: int) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(1, min(max_stage + 1, 7)):
        title = {
            1: "Ввод в должность",
            2: "КВЕСТ-Адаптация",
            3: "WELCOME - ТРЕНИНГ",
            4: "ОБУЧЕНИЕ",
            5: "РЕГЛАМЕНТЫ ОТДЕЛА",
            6: "ИСПЫТАТЕЛЬНЫЙ СРОК"
        }.get(i, f"Этап {i}")
        buttons.append([InlineKeyboardButton(text=f"📄 Этап {i}: {title}", callback_data=f"stage_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)