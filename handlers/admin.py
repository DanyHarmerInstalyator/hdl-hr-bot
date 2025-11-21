# handlers/admin.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import db

router = Router()

# ID администраторов
ADMIN_IDS = [951689513, 7779513913]

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    await message.answer(
        "👨‍💼 Панель администратора\n\n"
        "Доступные команды:\n"
        "/users - Список всех пользователей\n"
        "/userstats - Статистика по пользователям"
    )

@router.message(Command("users"))
async def show_all_users(message: Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    users = db.get_all_users()
    
    if not users:
        await message.answer("📭 Пользователей не найдено.")
        return
    
    response = "👥 Все пользователи:\n\n"
    for user in users:
        user_id, username, first_name, last_name, current_stage, created_at, completed_stages = user
        name = f"{first_name or ''} {last_name or ''}".strip() or "Не указано"
        response += f"👤 {name}\n"
        response += f"📱 @{username}\n" if username else ""
        response += f"🆔 ID: {user_id}\n"
        response += f"📊 Этап: {current_stage}\n"
        response += f"✅ Завершено этапов: {completed_stages}\n"
        response += f"📅 Регистрация: {created_at}\n"
        response += "─" * 30 + "\n"
    
    await message.answer(response)

@router.message(Command("userstats"))
async def user_statistics(message: Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    users = db.get_all_users()
    
    if not users:
        await message.answer("📭 Пользователей не найдено.")
        return
    
    # Статистика по этапам
    stage_stats = {}
    total_users = len(users)
    
    for user in users:
        current_stage = user[4]  # current_stage находится на 5-й позиции
        stage_stats[current_stage] = stage_stats.get(current_stage, 0) + 1
    
    response = "📈 Статистика пользователей:\n\n"
    response += f"👥 Всего пользователей: {total_users}\n\n"
    
    for stage in sorted(stage_stats.keys()):
        count = stage_stats[stage]
        percentage = (count / total_users) * 100 if total_users > 0 else 0
        response += f"Этап {stage}:\n"
        response += f"👤 Пользователей: {count} ({percentage:.1f}%)\n\n"
    
    await message.answer(response)

# Добавляем администраторов при импорте
for admin_id in ADMIN_IDS:
    if admin_id == 951689513:
        db.add_admin(admin_id, "darya29088")
    elif admin_id == 7779513913:
        db.add_admin(admin_id, "Instalyator")  
        