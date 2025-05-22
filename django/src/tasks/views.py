from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

from .models import Task, Category, TodoUser
from .serializers import TaskSerializer, CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        tg_username = self.request.query_params.get('tg_username')
        if not tg_username:
            return Task.objects.none()

        user = TodoUser.objects.filter(tg_username=tg_username).first()
        if not user:
            return Task.objects.none()

        tasks = Task.objects.filter(user=user, completed=False).order_by('-due_date').select_related('category')

        return tasks


    def create(self, request, *args, **kwargs):
        print(request.data)
        user, _ = TodoUser.objects.get_or_create(
            tg_username=request.data.get('tg_username'),
            defaults={
                'tg_id': request.data.get('tg_id'),
                'username': request.data.get('tg_username'),
                'first_name': request.data.get('first_name') if request.data.get('first_name') else '',
                'last_name': request.data.get('last_name') if request.data.get('last_name') else '',
            },
        )
        if user.tg_id != request.data.get('tg_id'):
            with transaction.atomic():
                user.tg_id = request.data.get('tg_id')
                user.save()

        category_id = Category.objects.get_or_create(name=request.data.get('category'))[0].id

        serializer_data = {
           **request.data,
           'category': category_id,
           'user': user.id,
        }
        serializer = self.get_serializer(
           data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
