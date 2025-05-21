from django.apps import AppConfig
from django.conf import settings
from celery import Celery


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        from .tasks import send_task_reminders
        from celery import current_app
        current_app.conf.beat_schedule = {
            'send-task-reminders-every-hour': {
                'task': 'tasks.tasks.send_task_reminders',
                'schedule': 3600.0,  # каждые 60 минут
            },
        }