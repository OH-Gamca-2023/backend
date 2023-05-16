from django.db.models import Q
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from disciplines.models import Category, Discipline
from disciplines.serializers import CategorySerializer, DisciplineSerializer


class CategoriesView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class DisciplinesView(generics.ListAPIView):
    serializer_class = DisciplineSerializer
    queryset = Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))
    pagination_class = LimitOffsetPagination


class DisciplineDetailView(generics.RetrieveAPIView):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
