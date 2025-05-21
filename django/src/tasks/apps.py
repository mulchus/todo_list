from django.apps import AppConfig
from django.conf import settings
from celery import current_app


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    @staticmethod
    def ready():
        current_app.conf.beat_schedule = {
            'send-task-reminders-every-second': {
                'task': 'tasks.tasks.send_task_reminders',
                'schedule': 1.0
            },
        }
