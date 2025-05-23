from datetime import datetime

from celery import shared_task
from django.contrib.sessions.backends import db
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Task
import httpx
import pytz


@shared_task
def send_task_reminders():
    now = timezone.now()
    tasks = Task.objects.filter(due_date__lte=now, completed=False).select_related('user')
    for task in tasks:
        with db.transaction.atomic():
            task.completed = True
            task.save()
        tz = pytz.timezone(settings.TIME_ZONE)
        message = (f"Напоминание о задаче:\n{task.title}\nОписание: {task.description}\n"
                   f"Категория: {task.category.name}\n"
                   f"Срок выполнения: {datetime.strftime(task.due_date.astimezone(tz), '%d.%m.%Y %H:%M')}\n"
        )
        try:
            with httpx.Client() as client:
                response = client.post(
                    settings.ENV.TELEBOT_API_URL,
                    json={
                        'message': message,
                        'tg_id': task.user.tg_id,
                    }
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            print(f'ERROR: {e}')
