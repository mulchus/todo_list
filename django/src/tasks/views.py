from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


class TaskViewSet(ModelViewSet):
   queryset = Task.objects.all()
   serializer_class = TaskSerializer

class CategoryViewSet(ModelViewSet):
   queryset = Category.objects.all()
   serializer_class = CategorySerializer
