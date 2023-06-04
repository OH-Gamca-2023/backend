from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.models import User

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
        if self.request.user.is_authenticated and (self.request.user.is_staff  or self.request.user.clazz.grade.is_teacher):
            return Discipline.objects.all()
        return Discipline.objects.filter(Q(date_published=True) | Q(details_published=True) | Q(results_published=True))

    @action(detail=True)
    def results(self, request):
        discipline = self.get_object()
        queryset = Result.objects.filter(discipline=discipline)
        serializer = ResultSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'delete'], name='Primary organiser')
    def primary_organiser(self, request, pk=None):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if not self.request.user.clazz.grade.is_teacher and not self.request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

        discipline = self.get_object()
        if request.method == 'GET':
            if discipline.primary_organiser is None:
                return Response("null")
            return Response(discipline.primary_organiser.pk)
        elif request.method == 'PUT':
            if not self.request.user.clazz.grade.is_organiser and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            po_pk = request.data['primary_organiser']
            if po_pk is None:
                return Response({'detail': 'Primary organiser cannot be null. Use DELETE to remove.'}, status=400)

            po = User.objects.filter(pk=po_pk).first()
            if po is None:
                return Response({'detail': 'Target user does not exist.'}, status=400)

            if po.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to assign other users as primary organiser.'}, status=403)

            if po == discipline.primary_organiser:
                return Response(DisciplineSerializer(discipline).data)

            discipline.primary_organiser = po
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)
        elif request.method == 'DELETE':
            if not self.request.user.clazz.grade.is_organiser and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            if discipline.primary_organiser is None:
                return Response({'detail': 'No primary organiser to delete.'}, status=404)
            if discipline.primary_organiser.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to remove other users as primary organiser.'}, status=403)

            discipline.primary_organiser = None
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)

    @action(detail=True, methods=['get', 'put', 'delete'], name='Organisers')
    def organisers(self, request, pk=None):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if not self.request.user.clazz.grade.is_teacher and not self.request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

        discipline = self.get_object()
        if request.method == 'GET':
            return Response([o.pk for o in discipline.organisers.all()])
        elif request.method == 'PUT':
            if not self.request.user.clazz.grade.is_organiser and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            organiser = request.data['organiser']
            if organiser is None:
                return Response({'detail': 'Organiser to add cannot be null.'}, status=400)

            organiser = User.objects.filter(pk=organiser).first()
            if organiser is None:
                return Response({'detail': 'Target user does not exist.'}, status=400)

            if organiser.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to assign other users as organiser.'}, status=403)

            if organiser in discipline.organisers.all():
                return Response(DisciplineSerializer(discipline).data)

            discipline.organisers.add(organiser)
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)
        elif request.method == 'DELETE':
            if not self.request.user.clazz.grade.is_organiser and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            organiser = request.data['organiser']
            if organiser is None:
                return Response({'detail': 'Organiser to remove cannot be null.'}, status=400)

            organiser = User.objects.filter(pk=organiser).first()
            if organiser is None:
                return Response({'detail': 'Target user does not exist.'}, status=400)

            if organiser.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to remove other users from organiser.'}, status=403)

            if organiser not in discipline.organisers.all():
                return Response({'detail': 'Target user is not an organiser.'}, status=400)

            discipline.organisers.remove(organiser)
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)

    @action(detail=True, methods=['get', 'put', 'delete'], name='Teacher supervisors')
    def teacher_supervisors(self, request, pk=None):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if not self.request.user.clazz.grade.is_teacher and not self.request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

        discipline = self.get_object()
        if request.method == 'GET':
            return Response([o.pk for o in discipline.teacher_supervisors.all()])
        elif request.method == 'PUT':
            if not self.request.user.clazz.grade.is_teacher and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            teacher = request.data['teacher']
            if teacher is None:
                return Response({'detail': 'Organiser to add cannot be null.'}, status=400)

            teacher = User.objects.filter(pk=teacher).first()
            if teacher is None:
                return Response({'detail': 'Target user does not exist.'}, status=400)

            if teacher.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to assign other users as supervising teachers.'}, status=403)

            if teacher in discipline.teacher_supervisors.all():
                return Response(DisciplineSerializer(discipline).data)

            discipline.teacher_supervisors.add(teacher)
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)
        elif request.method == 'DELETE':
            if not self.request.user.clazz.grade.is_teacher and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to perform this action.'}, status=403)

            teacher = request.data['teacher']
            if teacher is None:
                return Response({'detail': 'Teacher to remove cannot be null.'}, status=400)

            teacher = User.objects.filter(pk=teacher).first()
            if teacher is None:
                return Response({'detail': 'Target user does not exist.'}, status=400)

            if teacher.pk != self.request.user.pk and not self.request.user.has_perm('disciplines.modify_people'):
                return Response({'detail': 'You do not have permission to remove other users from supervising teachers.'}, status=403)

            if teacher not in discipline.organisers.all():
                return Response({'detail': 'Target user is not an organiser.'}, status=400)

            discipline.organisers.remove(teacher)
            discipline.save()
            return Response(DisciplineSerializer(discipline).data)


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    model = Result
    serializer_class = ResultSerializer
    pagination_class = LimitOffsetPagination
    queryset = Result.objects.filter(discipline__results_published=True)
