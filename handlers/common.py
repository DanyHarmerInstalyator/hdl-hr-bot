# handlers/common.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.reply import get_menu
from storage import user_stage


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    stage = user_stage.get(message.from_user.id, 1)
    await message.answer(
        "Привет! 👋 Я — Ассистент HR-отдела.\n"
        "Помогу вам пройти адаптацию в компании.",
        reply_markup=get_menu(stage=stage)
    )