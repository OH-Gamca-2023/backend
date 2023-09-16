from rest_framework import serializers

from backend.disciplines.models import Category, Discipline, Result, Placement
from backend.users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'calendar_class', 'icon')


class DisciplineSerializer(serializers.ModelSerializer):
    primary_organisers = UserSerializer(many=True, read_only=True, hide_confidential=True)
    teacher_supervisors = UserSerializer(many=True, read_only=True, hide_confidential=True)

    class Meta:
        model = Discipline
        fields = ('id', 'name', 'short_name', 'details', 'date', 'start_time', 'end_time', 'location', 'category',
                  'target_grades', 'is_public', 'date_published', 'details_published', 'results_published',
                  'primary_organisers', 'teacher_supervisors')

    def to_representation(self, instance):
        user = self.context.get('request').user
        representation = super().to_representation(instance)
        if not user.is_authenticated:
            representation.pop('primary_organisers')
            representation.pop('teacher_supervisors')
        else:
            if not user.has_perm('disciplines.view_primary_organisers'):
                representation.pop('primary_organisers')
            if not user.has_perm('disciplines.view_teacher_supervisors'):
                representation.pop('teacher_supervisors')
            if not user.has_perm('disciplines.view_hidden'):
                if not instance.date_published:
                    representation.pop('date')
                    representation.pop('start_time')
                    representation.pop('end_time')
                    representation.pop('location')
                if not instance.details_published:
                    representation.pop('details')

        return representation


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = ('clazz', 'place', 'participated')


class ResultSerializer(serializers.ModelSerializer):
    placements = PlacementSerializer(many=True, read_only=True)

    class Meta:
        model = Result
        fields = ('id', 'discipline', 'name', 'grades', 'placements')
