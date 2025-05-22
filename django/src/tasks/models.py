from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets


def generate_custom_id():
    return secrets.token_hex(16)


class Category(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=32, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TodoUser(AbstractUser):
    tg_username = models.CharField(
        unique=True,
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram username',
    )

    def __str__(self):
        return f"{self.username} {self.tg_username}"''


class Task(models.Model):
    id = models.CharField(primary_key=True, default=generate_custom_id, max_length=32, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(TodoUser, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title
