from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from disciplines.models import Category, Discipline, Result
from disciplines.serializers import CategorySerializer, DisciplineSerializer, ResultSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class DisciplineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DisciplineSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'target_grades']
    search_fields = ['name', 'details']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Discipline.objects.all()
        return Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))

    @action(detail=True)
    def results(self, request):
        discipline = self.get_object()
        queryset = Result.objects.filter(discipline=discipline)
        serializer = ResultSerializer(queryset, many=True)
        return Response(serializer.data)


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    model = Result
    serializer_class = ResultSerializer
    pagination_class = LimitOffsetPagination
    queryset = Result.objects.filter(discipline__results_published=True)
