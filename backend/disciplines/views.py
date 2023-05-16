from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
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
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'target_grades']
    search_fields = ['name', 'details']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Discipline.objects.all()
        return Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))


class DisciplineDetailView(generics.RetrieveAPIView):
    serializer_class = DisciplineSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Discipline.objects.all()
        return Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))
