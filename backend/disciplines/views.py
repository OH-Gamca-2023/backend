from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.disciplines.sidebar import SidebarObject, SidebarSerializer
from backend.users.models import User

from backend.disciplines.models import Category, Discipline, Result
from backend.disciplines.serializers import CategorySerializer, DisciplineSerializer, ResultSerializer


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
        if self.request.user.is_authenticated and (self.request.user.is_staff  or self.request.user.clazz.grade.is_teacher):
            return Discipline.objects.all()
        return Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))

    @action(detail=True)
    def results(self, request):
        discipline = self.get_object()
        queryset = Result.objects.filter(discipline=discipline)
        serializer = ResultSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put', 'delete'], name='Primary organisers')
    def primary_organisers(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if not request.user.clazz.grade.is_organiser and not request.user.has_perm('disciplines.modify_people'):
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

        discipline = self.get_object()
        if request.method == 'PUT':

            organiser = request.data['organiser']
            if organiser is None:
                return Response({'detail': 'Organiser to add cannot be null.'}, status=400)
            if organiser == 'me':
                organiser = request.user.pk

            organiser = User.objects.filter(pk=organiser).first()
            if organiser is None:
                return Response({'detail': 'Target user does not exist.'}, status=404)

            if organiser.pk != request.user.pk and not request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to assign other users as organiser.'}, status=403)

            if not organiser.clazz.grade.is_organiser:
                return Response({'detail': 'Target user is not an organiser.'}, status=400)

            if organiser in discipline.primary_organisers.all():
                return Response(DisciplineSerializer(discipline, context={'request': request}).data)

            discipline.primary_organisers.add(organiser)
            discipline.save()
            return Response(DisciplineSerializer(discipline, context={'request': request}).data)

        elif request.method == 'DELETE':

            organiser = request.data['organiser']
            if organiser is None:
                return Response({'detail': 'Organiser to remove cannot be null.'}, status=400)
            if organiser == 'me':
                organiser = request.user.pk

            organiser = User.objects.filter(pk=organiser).first()
            if organiser is None:
                return Response({'detail': 'Target user does not exist.'}, status=404)

            if organiser.pk != request.user.pk and not request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to remove other users from organiser.'}, status=403)

            if organiser not in discipline.primary_organisers.all():
                return Response({'detail': 'Target user is not a primary organiser.'}, status=400)

            discipline.primary_organisers.remove(organiser)
            discipline.save()
            return Response(DisciplineSerializer(discipline, context={'request': request}).data)

    @action(detail=True, methods=['put', 'delete'], name='Teacher supervisors')
    def teacher_supervisors(self, request, pk=None):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if not self.request.user.clazz.grade.is_teacher and not self.request.user.has_perm('disciplines.modify_people'):
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

        discipline = self.get_object()
        if request.method == 'PUT':

            teacher = request.data['teacher']
            if teacher is None:
                return Response({'detail': 'Teacher to add cannot be null.'}, status=400)

            teacher = User.objects.filter(pk=teacher).first()
            if teacher is None:
                return Response({'detail': 'Target user does not exist.'}, status=404)

            if teacher.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to assign other users as supervising teachers.'}, status=403)

            if not teacher.clazz.grade.is_teacher:
                return Response({'detail': 'Target user is not a teacher.'}, status=400)

            if teacher in discipline.teacher_supervisors.all():
                return Response(DisciplineSerializer(discipline, context={'request': request}).data)

            discipline.teacher_supervisors.add(teacher)
            discipline.save()
            return Response(DisciplineSerializer(discipline, context={'request': request}).data)

        elif request.method == 'DELETE':

            teacher = request.data['teacher']
            if teacher is None:
                return Response({'detail': 'Teacher to remove cannot be null.'}, status=400)

            teacher = User.objects.filter(pk=teacher).first()
            if teacher is None:
                return Response({'detail': 'Target user does not exist.'}, status=404)

            if teacher.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to remove other users from supervising teachers.'}, status=403)

            if teacher not in discipline.teacher_supervisors.all():
                return Response({'detail': 'Target user is not a supervising teacher.'}, status=400)

            discipline.teacher_supervisors.remove(teacher)
            discipline.save()
            return Response(DisciplineSerializer(discipline, context={'request': request}).data)


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    model = Result
    serializer_class = ResultSerializer
    pagination_class = LimitOffsetPagination
    queryset = Result.objects.filter(discipline__results_published=True)


class SidebarView(APIView):

    def get(self, request):
        return Response(SidebarSerializer(SidebarObject.get_sidebar_object(request), context={'request': request}).data)
