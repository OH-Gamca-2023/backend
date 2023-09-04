from datetime import datetime

from django.db.models import Q
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.disciplines.models import Discipline


class SidebarDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ('id', 'name', 'short_name', 'date', 'start_time', 'end_time', 'location', 'category', 'target_grades')


class SidebarObject:
    def __init__(self, upcoming: list[Discipline], organising: list[Discipline], supervising: list[Discipline]):
        self.upcoming = upcoming
        self.organising = organising
        self.supervising = supervising

    @staticmethod
    def get_sidebar_object(request):
        def filter_query():
            filter = Q(date__gte=datetime.now())
            if request.user.is_authenticated and request.user.clazz.grade.competing:
                filter |= Q(target_grades__contains=request.user.clazz.grade)
            if not (request.user.is_authenticated and request.user.has_perm('disciplines.view_hidden')):
                filter &= Q(date_published=True) & Q(details_published=True) & Q(results_published=True)
            return filter

        upcoming = Discipline.objects.filter(filter_query()).order_by('date', 'start_time')[:5]
        organising = []
        supervising = []

        if request.user.is_authenticated:
            if request.user.has_perm('disciplines.view_primary_organisers'):
                organising = Discipline.objects.filter(filter_query(), primary_organisers=request.user).order_by('date', 'start_time')[:5]
            if request.user.has_perm('disciplines.view_teacher_supervisors'):
                supervising = Discipline.objects.filter(filter_query(), teacher_supervisors=request.user).order_by('date', 'start_time')[:5]

        return SidebarObject(upcoming, organising, supervising)


class SidebarSerializer(serializers.Serializer):
    upcoming = SidebarDisciplineSerializer(many=True)
    organising = SidebarDisciplineSerializer(many=True)
    supervising = SidebarDisciplineSerializer(many=True)


class SidebarView(APIView):

    def get(self, request):
        return Response(SidebarSerializer(SidebarObject.get_sidebar_object(request), context={'request': request}).data)
