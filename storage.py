# storage.py
from database import db

def get_user_stage(user_id: int) -> int:
    """Получение текущего этапа пользователя"""
    try:
        return db.get_user_stage(user_id)
    except Exception as e:
        print(f"Ошибка получения этапа: {e}")
        return 1

def set_user_stage(user_id: int, stage: int):
    """Установка этапа пользователя"""
    try:
        db.set_user_stage(user_id, stage)
    except Exception as e:
        print(f"Ошибка установки этапа: {e}")

def mark_stage_completed(user_id: int, stage: int):
    """Отметить этап как завершенный"""
    try:
        db.mark_stage_completed(user_id, stage)
    except Exception as e:
        print(f"Ошибка отметки этапа: {e}")

def save_current_progress(user_id: int, stage: int, completed_tasks: list, pending_tasks: list):
    """Сохранить текущий прогресс по этапу"""
    try:
        db.save_current_progress(user_id, stage, completed_tasks, pending_tasks)
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")

def get_current_progress(user_id: int, stage: int) -> dict:
    """Получить текущий прогресс по этапу"""
    try:
        return db.get_current_progress(user_id, stage)
    except Exception as e:
        print(f"Ошибка получения прогресса: {e}")
        return {'completed_tasks': [], 'pending_tasks': []}

def get_user_completed_stages(user_id: int) -> list:
    """Получить список завершенных этапов"""
    try:
        return db.get_completed_stages(user_id)
    except Exception as e:
        print(f"Ошибка получения завершенных этапов: {e}")
        return []