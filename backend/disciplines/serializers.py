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

    def get_fields(self):
        fields = super().get_fields()
        # if user is logged in
        if not self.context['request'].user.is_authenticated:
            fields.pop('primary_organisers')
            fields.pop('teacher_supervisors')
        else:
            if not self.context['request'].user.has_perm('disciplines.view_primary_organisers'):
                fields.pop('primary_organisers')
            if not self.context['request'].user.has_perm('disciplines.view_teacher_supervisors'):
                fields.pop('teacher_supervisors')
            if not self.context['request'].user.has_perm('disciplines.view_hidden'):
                if not self.instance.date_published:
                    fields.pop('date')
                    fields.pop('start_time')
                    fields.pop('end_time')
                    fields.pop('location')
                if not self.instance.details_published:
                    fields.pop('details')

        return fields


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = ('clazz', 'place', 'participated')


class ResultSerializer(serializers.ModelSerializer):
    placements = PlacementSerializer(many=True, read_only=True)

    class Meta:
        model = Result
        fields = ('id', 'discipline', 'name', 'grades', 'placements')
