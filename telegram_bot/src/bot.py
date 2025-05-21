from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import CommandStart
import os
import asyncio
import aiohttp
import httpx


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://django/api/tasks/')
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()

async def fetch(session, method, endpoint, params=None, data=None):
    headers = {
        "Authorization": f"Bearer {API_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    print(method, DJANGO_API_URL + endpoint, params, data)
    async with session.request(method, DJANGO_API_URL + endpoint, json=data, params=params, headers=headers) as response:
        return await response.json(), response.status


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, работающий с вашим API.")


@dp.message(lambda m: "/tasks" in m.text.lower())
async def list_users(message: types.Message):
    async with aiohttp.ClientSession() as session:
        tasks_list, status_code = await fetch(session, "GET", "")
        print(tasks_list, status_code)
        if status_code == 200:
            message_tasks_list = "\n".join([f"{task['title']} ({task['due_date']})" for task in tasks_list])
            await message.answer(f"Список тасок:\n\n{message_tasks_list}")
        else:
            await message.answer(f"Произошла ошибка: {tasks_list.get('message', '')}. Код статуса: {status_code}")


@dp.message(lambda m: "/add_task" in m.text.lower())
async def task_details(message: types.Message):
    try:
        user_id = int(message.text.split()[1]) # получаем ID пользователя из команды /task id
    except ValueError:
        await message.answer("Ошибка формата команды. Используйте /task номер_пользователя")
        return

    async with aiohttp.ClientSession() as session:
        result, status_code = await fetch(session, "GET", f"tasks/{user_id}")
        if status_code == 200:
            tasks_list = "\n".join([f"- {t['title']}" for t in result["tasks"]])
            await message.answer(f"Тasks пользователя №{user_id}:\n\n{tasks_list}")
        else:
            await message.answer(f"Произошла ошибка: {result.get('message', '')}. Код статуса: {status_code}")


if __name__ == "__main__":
    print("Start telegram bot")
    asyncio.run(dp.start_polling(bot))
