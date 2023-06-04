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
                  'primary_organiser', 'organisers', 'teacher_supervisors')


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = ('clazz', 'place', 'participated')


class ResultSerializer(serializers.ModelSerializer):
    placements = PlacementSerializer(many=True, read_only=True)

    class Meta:
        model = Result
        fields = ('id', 'discipline', 'name', 'grades', 'placements')
