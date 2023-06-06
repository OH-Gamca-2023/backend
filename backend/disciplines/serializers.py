from rest_framework import serializers

from disciplines.models import Category, Discipline, Result, Placement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'calendar_class')


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ('id', 'name', 'short_name', 'details', 'date', 'time', 'location', 'volatile_date', 'category',
                  'target_grades', 'is_public', 'date_published', 'details_published', 'results_published',
                  'primary_organisers', 'teacher_supervisors')

    def get_fields(self):
        fields = super().get_fields()
        # if user is logged in
        if not self.context['request'].user.is_authenticated:
            fields.pop('primary_organisers')
            fields.pop('teacher_supervisors')
        elif not (self.context['request'].user.is_staff or self.context['request'].user.clazz.grade.is_teacher or \
                    self.context['request'].user.clazz.grade.is_organiser):
            fields.pop('primary_organisers')
            fields.pop('teacher_supervisors')

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
