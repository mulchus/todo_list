from datetime import datetime

from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from .models import Task, Category
import pytz


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    formatted_due_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'due_date',
            'completed',
            'category',
            'category_name',
            'user',
            'formatted_due_date'
        ]

    @staticmethod
    def get_formatted_due_date(obj):
        if obj.due_date:
            tz = pytz.timezone(settings.TIME_ZONE)
            obj.due_date = obj.due_date.astimezone(tz)
            return obj.due_date.strftime('%d.%m.%Y %H:%M')
        return None

    def to_internal_value(self, data):
        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%d.%m.%Y %H:%M')
                due_date = timezone.make_aware(due_date, timezone.get_current_timezone())
                data['due_date'] = due_date
            except ValueError:
                raise serializers.ValidationError({
                    'due_date': 'Неправильный формат datetime. Используйте формат DD.MM.YYYY HH:MM.'
                })

        return super().to_internal_value(data)
