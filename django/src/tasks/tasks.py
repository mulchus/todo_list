from celery import shared_task
from django.contrib.sessions.backends import db
from django.core.mail import send_mail
from django.utils import timezone
from .models import Task


@shared_task
def send_task_reminders():
    now = timezone.now()
    tasks = Task.objects.filter(due_date__lte=now, completed=False)
    print(f'FILTERED TASKS {tasks}')
    for task in tasks:
        # send_mail(
        #     'Task Reminder',
        #     f'Reminder: The task "{task.title}" is due.',
        #     'from@example.com',
        #     [task.user.email],
        #     fail_silently=False,
        # )
        print(f'REMINDER: The task "{task.title}" is due.', [task.user.email])
        with db.transaction.atomic():
            task.completed = True
            task.save()
