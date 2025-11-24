from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.bitrix import get_task_checklist, get_task_checklist_details, get_task_deadline
from storage import get_user_stage
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
    current_stage = get_user_stage(message.from_user.id)
    await message.answer(
        "Выберите этап для просмотра:",
        reply_markup=get_stage_inline_keyboard(max_stage=current_stage)
    )

# --- Обработчик: "✅ Проверить текущий этап" ---
@router.message(F.text == "✅ Проверить текущий этап")
async def check_current_stage(message: Message):
    current = get_user_stage(message.from_user.id)

    # --- Этап 1: проверка 5 блоков ---
    if current == 1:
        checklist = get_task_checklist(TASK_IDS[1])
        if not isinstance(checklist, dict):
            await message.answer("❌ Не удалось загрузить чек-лист этапа 1.")
            return

        completed_count, blocks = get_all_blocks_completion(checklist)
        if completed_count == 5:
            from storage import set_user_stage, mark_stage_completed, save_current_progress
            mark_stage_completed(message.from_user.id, current)
            set_user_stage(message.from_user.id, 2)
            
            # Получаем дедлайн для этапа 2
            deadline = get_task_deadline(TASK_IDS[2])
            deadline_text = f"⏰ Дедлайн этапа 2: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
            
            # Первое сообщение - поздравление
            await message.answer(
                "✅ Все 5 блоков этапа 1 завершены!\n"
                "🎉 Поздравляем! Теперь доступен <b>Этап 2: КВЕСТ-Адаптация</b>.",
                parse_mode="HTML"
            )
            
            # Второе сообщение - ссылка и дедлайн
            await message.answer(
                "🔗 <b>Ссылка на Этап 2:</b>\n"
                "https://hdl.bitrix24.ru/company/personal/user/4057/tasks/task/view/82127/\n\n"
                f"{deadline_text}",
                parse_mode="HTML"
            )
            
            # Третье сообщение - описание этапа
            stage2_info = (
                "🎯 <b>Этап 2: КВЕСТ-Адаптация</b>\n\n"
                "В этом этапе вам предстоит:\n"
                "• Познакомиться с коллегами\n"
                "• Изучить рабочие процессы\n"
                "• Пройти вводный инструктаж\n"
                "• Получить доступы к системам\n\n"
                "ℹ️ <i>Выполняйте задания по порядку и отмечайте их выполнение в чек-листе</i>"
            )
            await message.answer(stage2_info, parse_mode="HTML")
            
        else:
            from storage import save_current_progress
            # Сохраняем прогресс в БД
            completed_tasks = []
            pending_tasks = []
            
            for b in blocks:
                if b["completed"]:
                    completed_tasks.append(f"Блок №{b['num']}")
                else:
                    pending_tasks.append(f"Блок №{b['num']}: {', '.join(b['missing'])}")
            
            save_current_progress(message.from_user.id, current, completed_tasks, pending_tasks)
            
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

        from storage import set_user_stage, mark_stage_completed, save_current_progress
        
        # Сохраняем прогресс в БД
        completed_tasks = [item["title"] for item in details if item["completed"]]
        pending_tasks = [item["title"] for item in details if not item["completed"]]
        
        save_current_progress(message.from_user.id, current, completed_tasks, pending_tasks)
        
        not_completed = [item for item in details if not item["completed"]]
        if not not_completed:
            # Успех
            mark_stage_completed(message.from_user.id, current)
            
            if current == 6:
                set_user_stage(message.from_user.id, 7)
                await message.answer("🎉 Поздравляем! Вы успешно завершили всю адаптацию!")
            else:
                next_stage = current + 1
                set_user_stage(message.from_user.id, next_stage)
                next_title = STAGE_TITLES[next_stage]
                
                # Получаем дедлайн для следующего этапа
                deadline = get_task_deadline(TASK_IDS[next_stage])
                deadline_text = f"⏰ Дедлайн этапа {next_stage}: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
                
                await message.answer(
                    f"✅ Этап {current} завершён!\n"
                    f"🎉 Доступен <b>Этап {next_stage}: {next_title}</b>.",
                    parse_mode="HTML"
                )
                await message.answer(
                    f"🔗 <b>Ссылка на Этап {next_stage}:</b>\n"
                    f"https://hdl.bitrix24.ru/company/personal/user/4057/tasks/task/view/{TASK_IDS[next_stage]}/\n\n"
                    f"{deadline_text}",
                    parse_mode="HTML"
                )
                
                # Добавляем описание для конкретных этапов
                if next_stage == 2:
                    stage_info = (
                        "🎯 <b>Этап 2: КВЕСТ-Адаптация</b>\n\n"
                        "В этом этапе вам предстоит:\n"
                        "• Познакомиться с коллегами\n"
                        "• Изучить рабочие процессы\n"
                        "• Пройти вводный инструктаж\n"
                        "• Получить доступы к системам\n\n"
                        "ℹ️ <i>Выполняйте задания по порядку и отмечайте их выполнение в чек-листе</i>"
                    )
                    await message.answer(stage_info, parse_mode="HTML")
                elif next_stage == 3:
                    stage_info = (
                        "🎯 <b>Этап 3: WELCOME - ТРЕНИНГ.</b>\n\n"
                        "В этом этапе вам предстоит:\n"
                        "• Пройти Welcome-тренинг: История Группы компаний\n"
                        "• Прочитать письма от собственника бизнеса\n\n"
                        "ℹ️ <i>Выполняйте задания по порядку и отмечайте их выполнение в чек-листе</i>"
                    )
                    await message.answer(stage_info, parse_mode="HTML")
                elif next_stage == 4:
                    stage_info = (
                        "🎯 <b>Этап 4: ОБУЧЕНИЕ</b>\n\n"
                        "В этом этапе вам предстоит:\n"
                        "• Пройти дистанционное обучение в Битрикс24\n"
                        "• Изучить видеоуроки по работе с системой\n"
                        "• Освоить основные бизнес-процессы компании\n\n"
                        "ℹ️ <i>Обучение проходит в проекте 'ОБУЧЕНИЕ БИТРИКС24'</i>"
                    )
                    await message.answer(stage_info, parse_mode="HTML")
                elif next_stage == 5:
                    stage_info = (
                        "🎯 <b>Этап 5: РЕГЛАМЕНТЫ ОТДЕЛА</b>\n\n"
                        "В этом этапе вам предстоит:\n"
                        "• Изучить регламенты, инструкции и скрипты отдела\n"
                        "• Понять роль наставника в компании\n"
                        "• Освоить внутренние процессы и правила\n\n"
                        "ℹ️ <i>Внимательно изучите все документы вашего отдела</i>"
                    )
                    await message.answer(stage_info, parse_mode="HTML")
                elif next_stage == 6:
                    stage_info = (
                        "🎯 <b>Этап 6: ИСПЫТАТЕЛЬНЫЙ СРОК</b>\n\n"
                        "В этом этапе вам предстоит:\n"
                        "• Подготовить отчет по результатам испытательного срока\n"
                        "• Пройти оценку деятельности за период адаптации\n"
                        "• Получить финальную обратную связь\n\n"
                        "ℹ️ <i>Это завершающий этап вашей адаптации в компании</i>"
                    )
                    await message.answer(stage_info, parse_mode="HTML")
                    
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
    stage = get_user_stage(message.from_user.id)
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
    task_url = f"https://hdl.bitrix24.ru/company/personal/user/4057/tasks/task/view/{task_id}/"
    await callback.message.answer(
        f"🔗 <b>Переход к задаче:</b>\n<a href='{task_url}'>Этап {stage}: {STAGE_TITLES[stage]}</a>",
        parse_mode="HTML"
    )

    # 2. Для этапа 1 — отправляем документы и дедлайн
    if stage == 1:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"

        docs_message = (
            f"{deadline_text}\n\n"

            "📄 <b>Блок №1.2: Заполнить и подписать Заявление — согласие на обработку персональных данных</b>\n"
            '<a href="https://disk.360.yandex.ru/i/-qH3PaGWGpaOlQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.4: Подписать договор о неразглашении информации, являющейся коммерческой тайной в организации</b>\n"
            '<a href="https://disk.360.yandex.ru/i/gbNMIv88GaWRGQ">Скачать Документ</a>\n\n'

            "📄 <b>Блок №2.8: Подписать Лист ознакомления с ЛНА</b>\n"
            '<a href="https://disk.360.yandex.ru/i/mW50gaBs1yTuIw">Скачать Документ</a>\n\n'

            "ℹ️ <i>Все документы необходимо отсканировать и сохранить в комментариях к задаче в Битриксе на рабочем компьютере.</i>"
        )
        await callback.message.answer(docs_message, parse_mode="HTML")

    # 3. Для этапа 2 — отправляем дедлайн и описание
    elif stage == 2:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа 2: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
        
        stage2_message = (
            f"{deadline_text}\n\n"
            "🎯 <b>Этап 2: КВЕСТ-Адаптация</b>\n\n"
            "В этом этапе вам предстоит:\n"
            "• Познакомиться с коллегами\n"
            "• Изучить рабочие процессы\n"
            "• Пройти вводный инструктаж\n"
            "• Получить доступы к системам\n\n"
            "ℹ️ <i>Выполняйте задания по порядку и отмечайте их выполнение в чек-листе</i>"
        )
        await callback.message.answer(stage2_message, parse_mode="HTML")

    # 4. Для этапа 3 — отправляем дедлайн и описание
    elif stage == 3:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа 3: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
        
        stage3_message = (
            f"{deadline_text}\n\n"
            "🎯 <b>Этап 3: WELCOME - ТРЕНИНГ.</b>\n\n"
            "В этом этапе вам предстоит:\n"
            "• Пройти Welcome-тренинг: История Группы компаний\n"
            "• Прочитать письма от собственника бизнеса\n\n"
            "ℹ️ <i>Выполняйте задания по порядку и отмечайте их выполнение в чек-листе</i>"
        )
        await callback.message.answer(stage3_message, parse_mode="HTML")

    # 5. Для этапа 4 — отправляем дедлайн и описание
    elif stage == 4:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа 4: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
        
        stage4_message = (
            f"{deadline_text}\n\n"
            "🎯 <b>Этап 4: ОБУЧЕНИЕ</b>\n\n"
            "В этом этапе вам предстоит:\n"
            "• Пройти дистанционное обучение в Битрикс24\n"
            "• Изучить видеоуроки по работе с системой\n"
            "• Освоить основные бизнес-процессы компании\n\n"
            "ℹ️ <i>Обучение проходит в проекте 'ОБУЧЕНИЕ БИТРИКС24'</i>"
        )
        await callback.message.answer(stage4_message, parse_mode="HTML")

    # 6. Для этапа 5 — отправляем дедлайн и описание
    elif stage == 5:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа 5: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
        
        stage5_message = (
            f"{deadline_text}\n\n"
            "🎯 <b>Этап 5: РЕГЛАМЕНТЫ ОТДЕЛА</b>\n\n"
            "В этом этапе вам предстоит:\n"
            "• Изучить регламенты, инструкции и скрипты отдела\n"
            "• Понять роль наставника в компании\n"
            "• Освоить внутренние процессы и правила\n\n"
            "ℹ️ <i>Внимательно изучите все документы вашего отдела</i>"
        )
        await callback.message.answer(stage5_message, parse_mode="HTML")

    # 7. Для этапа 6 — отправляем дедлайн и описание
    elif stage == 6:
        deadline = get_task_deadline(task_id)
        deadline_text = f"⏰ Дедлайн этапа 6: Крайний срок: {deadline}" if deadline else "⏰ Дедлайн: не указан"
        
        stage6_message = (
            f"{deadline_text}\n\n"
            "🎯 <b>Этап 6: ИСПЫТАТЕЛЬНЫЙ СРОК</b>\n\n"
            "В этом этапе вам предстоит:\n"
            "• Подготовить отчет по результатам испытательного срока\n"
            "• Пройти оценку деятельности за период адаптации\n"
            "• Получить финальную обратную связь\n\n"
            "ℹ️ <i>Это завершающий этап вашей адаптации в компании</i>"
        )
        await callback.message.answer(stage6_message, parse_mode="HTML")

    await callback.answer()