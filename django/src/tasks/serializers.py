from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'completed', 'category', 'user']
