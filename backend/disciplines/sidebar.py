from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from backend.disciplines.models import Discipline


class SidebarDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ('id', 'name', 'short_name', 'date', 'time', 'location', 'category', 'target_grades')


class SidebarObject:
    def __init__(self, upcoming: list[Discipline], organising: list[Discipline], supervising: list[Discipline]):
        self.upcoming = upcoming
        self.organising = organising
        self.supervising = supervising

    @staticmethod
    def get_sidebar_object(request):
        def filter_query():
            if request.user.is_authenticated:
                if request.user.has_perm('disciplines.view_hidden'):
                    return Q(date__gte=datetime.now())
            return Q(date__gte=datetime.now()) & (Q(date_published=True) | Q(details_published=True) | Q(results_published=True))

        upcoming = Discipline.objects.filter(filter_query()).order_by('date')[:5]
        organising = []
        supervising = []

        if request.user.is_authenticated:
            if request.user.has_perm('disciplines.view_primary_organisers'):
                organising = Discipline.objects.filter(filter_query(), primary_organisers=request.user).order_by('date')[:5]
            if request.user.has_perm('disciplines.view_teacher_supervisors'):
                supervising = Discipline.objects.filter(filter_query(), teacher_supervisors=request.user).order_by('date')[:5]

        return SidebarObject(upcoming, organising, supervising)


class SidebarSerializer(serializers.Serializer):
    upcoming = SidebarDisciplineSerializer(many=True)
    organising = SidebarDisciplineSerializer(many=True)
    supervising = SidebarDisciplineSerializer(many=True)
