from django.contrib import admin
from .models import Task, Category, TodoUser


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'completed', 'user')
    list_filter = ('completed', 'due_date')
    search_fields = ('title', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TodoUser)
class TodoUserAdmin(admin.ModelAdmin):
    list_display = ('tg_username', 'username', 'first_name', 'last_name', )
    search_fields = ('tg_username', 'username', 'first_name', 'last_name', )
