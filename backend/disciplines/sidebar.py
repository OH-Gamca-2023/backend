from datetime import datetime

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
        if request.user.is_authenticated:
            upcoming = Discipline.objects.filter(date__gte=datetime.now()).order_by('date')[:5]
            organising = Discipline.objects.filter(primary_organisers=request.user,
                                                   date__gte=datetime.now()).order_by('date')[:5]
            supervising = Discipline.objects.filter(teacher_supervisors=request.user,
                                                    date__gte=datetime.now()).order_by('date')[:5]
        else:
            upcoming = Discipline.objects.filter(date__gte=datetime.now(), is_public=True).order_by('date')[:5]
            organising = []
            supervising = []
        return SidebarObject(upcoming, organising, supervising)


class SidebarSerializer(serializers.Serializer):
    upcoming = SidebarDisciplineSerializer(many=True)
    organising = SidebarDisciplineSerializer(many=True)
    supervising = SidebarDisciplineSerializer(many=True)
