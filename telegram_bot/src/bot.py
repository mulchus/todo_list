from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.filters import Command
from aiogram.filters.state import StatesGroup, State

from aiogram_dialog import Dialog, DialogManager, setup_dialogs, StartMode, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Next, Row, Calendar
from aiogram_dialog.widgets.input import TextInput

from remainder import make_quart_app

import os
import asyncio
import httpx


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://django/api/tasks/')


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
quart_app = make_quart_app(bot)


class SG(StatesGroup):
    main_menu = State()
    show_tasks = State()
    add_task = State()
    add_task_title = State()
    add_task_description = State()
    add_task_category = State()
    add_task_due_date = State()


async def show_tasks(
        event: Message, widget, dialog_manager: DialogManager,
        **kwargs,
):
    try:
        with httpx.Client() as client:
            response = client.get(
                DJANGO_API_URL,
                params={"tg_username": dialog_manager.event.from_user.username},
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        await bot.send_message(
            dialog_manager.event.from_user.id,
            f"Ошибка получения задач: {e}"
        )
        await bot.delete_message(chat_id=event.message.chat.id, message_id=event.message.message_id)
        await dialog_manager.start(SG.main_menu)
        return

    tasks = response.json()
    task_list = "\n".join(
        [f"\n{task['title']}, (категория: {task['category_name']}, "
         f"срок: {task['formatted_due_date']})"
         for task in tasks])
    await bot.delete_message(chat_id=event.message.chat.id, message_id=event.message.message_id)
    if not task_list:
        await bot.send_message(
            dialog_manager.event.from_user.id,
            "У вас нет незавершенных задач.",
        )
    else:
        await bot.send_message(
            dialog_manager.event.from_user.id,
            f"Задачи: {task_list}"
        )


async def add_task(
        event: Message, widget, dialog_manager: DialogManager,
        category: str,
        **kwargs,
):
    data = dialog_manager.current_context().widget_data
    due_date = data.get('task_due_date')

    try:
        datetime.strptime(due_date, "%d.%m.%Y %H:%M")
    except ValueError:
        await bot.send_message(
            dialog_manager.event.from_user.id,
            f"Ошибка сохранения задачи: неверный формат даты"
        )
        await dialog_manager.switch_to(SG.add_task_due_date)
        return

    if datetime.strptime(due_date, "%d.%m.%Y %H:%M") <= datetime.now():
        await bot.send_message(
            dialog_manager.event.from_user.id,
            f"Ошибка сохранения задачи: дата и время не могут быть меньше текущих."
        )
        await dialog_manager.switch_to(SG.add_task_due_date)
        return

    title = data.get('task_title')
    category = data.get('task_category')
    description = data.get('task_description')

    try:
        with httpx.Client() as client:
            response = client.post(
                DJANGO_API_URL,
                json={
                    "title": title,
                    "description": description,
                    "category": category,
                    "due_date": due_date,
                    "tg_username": dialog_manager.event.from_user.username,
                    "tg_id": dialog_manager.event.from_user.id,
                    "last_name": dialog_manager.event.from_user.last_name,
                    "first_name": dialog_manager.event.from_user.first_name,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        await bot.send_message(
            dialog_manager.event.from_user.id,
            f"Ошибка сохранения задачи: {e}"
        )
        await dialog_manager.done()
        await dialog_manager.start(SG.main_menu)
        return

    await bot.send_message(
       dialog_manager.event.from_user.id,
       f"Задача '{title}' '{due_date}' успешно добавлена!"
    )
    await dialog_manager.done()
    await dialog_manager.start(SG.main_menu)


dialog = Dialog(
    Window(Const("Главное меню"),
           Row(Button(Const("Показать задачи"), id="show_tasks", on_click=show_tasks),
               Button(Const("Добавить задачу"), id="add_task", on_click=Next())),
           state=SG.main_menu,
           ),
    Window(
        Const("Добавление новой задачи\n\nВведите название задачи:"),
        TextInput(id="task_title", on_success=Next()),
        Cancel(Const("Отмена")),
        state=SG.add_task_title,
    ),
    Window(
        Const("Введите описание задачи:"),
        TextInput(id="task_description", on_success=Next()),
        Cancel(Const("Отмена")),
        state=SG.add_task_description,
    ),
    Window(
        Const("Введите категорию задачи:"),
        TextInput(id="task_category", on_success=Next()),
        Cancel(Const("Отмена")),
        state=SG.add_task_category,
    ),
    # TODO: перевести на выбор из календаря
    Window(
        Const("Введите дату и время напоминания в формате '01.02.2025 15:15'"),
        TextInput(id="task_due_date", on_success=add_task),
        Cancel(Const("Отмена")),
        state=SG.add_task_due_date,
    )
    # TODO: перевести на выбор из календаря
    # Window(
    #     Const("Выберите дату и время напоминания:"),
    #     Calendar(id='task_due_date', on_click=add_task),
    #     Cancel(Const("Отмена")),
    #     state=SG.add_task_due_date,
    # ),
    )


dp.include_router(dialog)
setup_dialogs(dp)


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(SG.main_menu, mode=StartMode.RESET_STACK)


async def main():
    print("Start bots")
    await asyncio.gather(
        quart_app.run_task(host='0.0.0.0', port=5000),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())
