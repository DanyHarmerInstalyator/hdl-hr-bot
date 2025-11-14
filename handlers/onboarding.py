from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.bitrix import get_task_checklist, get_task_checklist_details, get_task_deadline
from storage import user_stage
from keyboards.inline import get_stage_inline_keyboard
from config_tasks import TASK_IDS, STAGE_TITLES

router = Router()

# --- Вспомогательная функция: проверка всех 5 блоков этапа 1 ---
def get_all_blocks_completion(checklist_dict: dict):
    blocks = []
    for block_num in range(1, 6):
        target_title = f"Блок № {block_num}"
        block_id = None
        for item in checklist_dict.values():
            title = item.get("title", "")
            if title.replace(" ", "") == target_title.replace(" ", "") and item.get("parentId") == 0:
                block_id = item["id"]
                break

        if not block_id:
            blocks.append({"num": block_num, "completed": False, "missing": []})
            continue

        items = [item for item in checklist_dict.values() if item.get("parentId") == block_id]
        not_completed = [item for item in items if item.get("isComplete") != "Y"]
        completed = len(not_completed) == 0
        missing_titles = [item["title"] for item in not_completed]

        blocks.append({
            "num": block_num,
            "completed": completed,
            "missing": missing_titles
        })

    completed_count = sum(1 for b in blocks if b["completed"])
    return completed_count, blocks

# --- Обработчик: "📂 Выбрать этап" ---
@router.message(F.text == "📂 Выбрать этап")
async def choose_stage(message: Message):
    current_stage = user_stage.get(message.from_user.id, 1)
    await message.answer(
        "Выберите этап для просмотра:",
        reply_markup=get_stage_inline_keyboard(max_stage=current_stage)
    )

# --- Обработчик: "✅ Проверить текущий этап" ---
@router.message(F.text == "✅ Проверить текущий этап")
async def check_current_stage(message: Message):
    current = user_stage.get(message.from_user.id, 1)

    # --- Этап 1: проверка 5 блоков ---
    if current == 1:
        checklist = get_task_checklist(TASK_IDS[1])
        if not isinstance(checklist, dict):
            await message.answer("❌ Не удалось загрузить чек-лист этапа 1.")
            return

        completed_count, blocks = get_all_blocks_completion(checklist)
        if completed_count == 5:
            user_stage[message.from_user.id] = 2
            await message.answer(
                "✅ Все 5 блоков этапа 1 завершены!\n"
                "🎉 Поздравляем! Теперь доступен <b>Этап 2: КВЕСТ-Адаптация</b>.",
                parse_mode="HTML"
            )
            await message.answer(
                "🔗 <b>Ссылка на Этап 2:</b>\n"
                "https://hdl.bitrix24.ru/company/personal/user/1673/tasks/task/view/79281/",
                parse_mode="HTML"
            )
        else:
            report = []
            for b in blocks:
                mark = "✅" if b["completed"] else "❌"
                line = f"{mark} Блок №{b['num']}"
                if b["missing"]:
                    missing_list = "\n    • ".join(b["missing"])
                    line += f"\n    • {missing_list}"
                report.append(line)
            await message.answer(
                f"⚠️ Завершено блоков: {completed_count} из 5\n\n" +
                "\n\n".join(report) + "\n\n" +
                "Пожалуйста, завершите все блоки и нажмите «Проверить текущий этап» снова."
            )

    # --- Этапы 2–6: проверка всех пунктов чек-листа ---
    elif 2 <= current <= 6:
        details = get_task_checklist_details(TASK_IDS[current])
        if details is None:
            await message.answer(f"❌ Не удалось загрузить чек-лист этапа {current}.")
            return

        not_completed = [item for item in details if not item["completed"]]
        if not not_completed:
            # Успех
            user_stage[message.from_user.id] = current + 1
            if current == 6:
                await message.answer("🎉 Поздравляем! Вы успешно завершили всю адаптацию!")
            else:
                next_stage = current + 1
                next_title = STAGE_TITLES[next_stage]
                await message.answer(
                    f"✅ Этап {current} завершён!\n"
                    f"🎉 Доступен <b>Этап {next_stage}: {next_title}</b>.",
                    parse_mode="HTML"
                )
                await message.answer(
                    f"🔗 <b>Ссылка на Этап {next_stage}:</b>\n"
                    f"https://hdl.bitrix24.ru/company/personal/user/1673/tasks/task/view/{TASK_IDS[next_stage]}/",
                    parse_mode="HTML"
                )
        else:
            # Ошибка — формируем отчёт
            report_lines = []
            for item in details:
                mark = "✅" if item["completed"] else "❌"
                report_lines.append(f"{mark} {item['title']}")
            report_text = "\n".join(report_lines)
            await message.answer(
                f"⚠️ В задаче этапа {current} остались незавершённые пункты:\n\n"
                f"{report_text}\n\n"
                "Пожалуйста, завершите все пункты и нажмите «Проверить текущий этап» снова."
            )

    else:
        await message.answer("🎉 Вы уже завершили всю адаптацию!")
        
# --- Обработчик: "❓ Задать вопрос HR-менеджеру" ---        
@router.message(F.text == "❓ Задать вопрос HR-менеджеру")
async def contact_hr(message: Message):
    await message.answer(
        "📩 Вы можете написать HR-менеджеру Дарье:\n"
        "👉 <a href='https://t.me/daryahr29088'>Открыть чат с Дарьей</a>\n\n"
        "Или нажмите на кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать Дарье", url="https://t.me/daryahr29088")]
        ]),
        parse_mode="HTML"
    )

# --- Обработчик: "📊 Мой прогресс" ---
@router.message(F.text == "📊 Мой прогресс")
async def show_progress(message: Message):
    stage = user_stage.get(message.from_user.id, 1)
    if stage == 1:
        checklist = get_task_checklist(TASK_IDS[1])
        if isinstance(checklist, dict):
            completed, _ = get_all_blocks_completion(checklist)
            await message.answer(f"📈 Этап 1: завершено блоков {completed} из 5")
        else:
            await message.answer("📈 Этап 1: в работе")
    elif stage <= 6:
        await message.answer(f"📈 Текущий этап: {stage - 1} (завершён)\nСледующий: Этап {stage}")
    else:
        await message.answer("🎉 Адаптация полностью завершена!")
# --- Обработчик нажатия на inline-кнопку этапа ---
@router.callback_query(F.data.startswith("stage_"))
async def handle_stage_inline(callback: CallbackQuery):
    stage_str = callback.data.split("_")[1]
    try:
        stage = int(stage_str)
    except ValueError:
        await callback.answer("Неверный этап", show_alert=True)
        return

    task_id = TASK_IDS.get(stage)
    if not task_id:
        await callback.answer("Этап не найден", show_alert=True)
        return

    # 1. Сначала — ссылка на задачу
    task_url = f"https://hdl.bitrix24.ru/company/personal/user/1673/tasks/task/view/{task_id}/"
    await callback.message.answer(
        f"🔗 <b>Переход к задаче:</b>\n<a href='{task_url}'>Этап {stage}: {STAGE_TITLES[stage]}</a>",
        parse_mode="HTML"
    )

    # 2. Только для этапа 1 — отправляем документы и дедлайн
    if stage == 1:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"

        docs_message = (
            f"{deadline_text}\n\n"

            "📄 <b>Блок №1.1: Ознакомление с регламентом</b>\n"
            '<a href="https://disk.360.yandex.ru/i/p4v8XQjs4mhAMg">Скачать Документ</a>\n\n'

            "📄 <b>Блок №1.2: Заполнить и подписать Заявление — согласие на обработку персональных данных</b>\n"
            '<a href="https://disk.360.yandex.ru/i/-qH3PaGWGpaOlQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.1: Ознакомиться с Правилами внутреннего трудового распорядка (ПВТР)</b>\n"
            '<a href="https://disk.360.yandex.ru/i/uNAVvUfhbaBiPQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.2: Ознакомиться с Положением об оплате труда и премировании ред.1.</b>\n"
            '<a href="https://disk.360.yandex.ru/i/tHULXrI-OqBRbA">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.3: Ознакомиться с Положением о коммерческой тайне</b>\n"
            '<a href="https://disk.360.yandex.ru/i/_A8aaf_ofv_CBQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.4: Подписать договор о неразглашении информации, являющейся коммерческой тайной в организации</b>\n"
            '<a href="https://disk.360.yandex.ru/i/gbNMIv88GaWRGQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.5: Ознакомиться с Положением по охране труда</b>\n"
            '<a href="https://disk.360.yandex.ru/i/g01IpK74R6FCHw">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.6: Ознакомиться с Инструкцией об охране труда</b>\n"
            '<a href="https://disk.360.yandex.ru/i/RQB50fx5k_ynaQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.7: Ознакомиться с Положением о Этике и Дресс-код</b>\n"
            '<a href="https://disk.360.yandex.ru/i/TNgXrA68TpDqXg">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.8: Подписать Лист ознакомления с ЛНА</b>\n"
            '<a href="https://disk.360.yandex.ru/i/mW50gaBs1yTuIw">Скачать Документ</a>\n\n'

            "ℹ️ <i>Все документы необходимо отсканировать и сохранить в комментариях к задаче в Битриксе на рабочем компьютере.</i>"
        )
        await callback.message.answer(docs_message, parse_mode="HTML")

    await callback.answer()

    # Отправляем доп. информацию только для этапа 1
    # if stage == 1:
    #     deadline = get_task_deadline(task_id)
    #     deadline_text = f"⏰ Дедлайн этапа: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"

    #     docs_text = (
    #         f"{deadline_text}\n\n"
    #         "📄 <b>Блок №1.1: Ознакомление с регламентом</b>\n"
    #         '<a href="https://disk.360.yandex.ru/i/p4v8XQjs4mhAMg">Скачать Документ</a>\n\n'
    #         "📄 <b>Блок №1.2: Заполнить и подписать Заявление — согласие на обработку персональных данных</b>\n"
    #         '<a href="https://disk.360.yandex.ru/i/-qH3PaGWGpaOlQ">Скачать Документ</a>\n\n'
    #         "ℹ️ <i>Все документы необходимо отсканировать и сохранить в комментариях к задаче в Битриксе на рабочем компьютере.</i>"
    #     )
    #     await callback.message.answer(docs_text, parse_mode="HTML")

    # Всегда отправляем ссылку на задачу
    task_url = f"https://hdl.bitrix24.ru/company/personal/user/1673/tasks/task/view/{task_id}/"
    await callback.message.answer(
        f"🔗 <b>Переход к задаче:</b>\n<a href='{task_url}'>Этап {stage}: {STAGE_TITLES[stage]}</a>",
        parse_mode="HTML"
    )

    await callback.answer()  # убираем "часики" на кнопке        