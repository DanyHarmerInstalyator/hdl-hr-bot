# utils/bitrix.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL")


def is_task_checklist_completed(task_id: int) -> bool | None:
    """
    Проверяет, завершены ли ВСЕ пункты в чек-листе задачи.
    Возвращает:
      - True: все выполнены
      - False: есть незавершённые
      - None: ошибка или нет чек-листа
    """
    checklist = get_task_checklist(task_id)
    if checklist is None:
        return None

    if not isinstance(checklist, dict):
        return None

    if not checklist:  # пустой чек-лист
        return True

    for item in checklist.values():
        # Пропускаем заголовки блоков (у них parentId == 0)
        if item.get("parentId") == 0:
            continue
        if item.get("isComplete") != "Y":
            return False

    return True

# utils/bitrix.py

def get_task_deadline(task_id: int) -> str | None:
    """Возвращает дедлайн задачи в формате '31.10.2025 19:00' или None."""
    url = f"{BITRIX_WEBHOOK_URL}tasks.task.get.json"
    params = {"taskId": task_id, "select[0]": "DEADLINE"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        deadline = data.get("result", {}).get("task", {}).get("deadline")
        if deadline:
            # Пример: "2025-10-31T19:00:00+03:00" → "31.10.2025 19:00"
            from datetime import datetime
            dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y %H:%M")
        return None
    except Exception as e:
        print(f"❌ Ошибка получения дедлайна: {e}")
        return None

def get_task_checklist_details(task_id: int):
    """
    Возвращает список всех пунктов чек-листа (игнорируя заголовки блоков),
    с указанием статуса выполнения.
    Формат: [{"title": "...", "completed": True/False}, ...]
    """
    checklist = get_task_checklist(task_id)
    if not isinstance(checklist, dict):
        return None

    items = []
    for item in checklist.values():
        if item.get("parentId") == 0:  # это заголовок блока — пропускаем
            continue
        items.append({
            "title": item.get("title", "Без названия"),
            "completed": item.get("isComplete") == "Y"
        })
    return items
# utils/bitrix.py
def get_task_checklist(task_id: int):
    url = f"{BITRIX_WEBHOOK_URL}tasks.task.get.json"
    params = {"taskId": task_id, "select[0]": "CHECKLIST"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        task = data.get("result", {}).get("task", {})
        checklist = task.get("checklist")

        # Bitrix24 возвращает checklist как dict (не list!)
        if isinstance(checklist, dict):
            return checklist
        else:
            print(f"⚠️ Неожиданный тип checklist: {type(checklist)}")
            return {}

    except Exception as e:
        print(f"❌ Ошибка Bitrix24: {e}")
        return None