from rest_framework import serializers

from backend.users.models import User, Clazz, Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('id', 'name')


class ClazzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clazz
        fields = ('id', 'name', 'grade', 'is_fake')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'clazz', 'microsoft_user', 'type', 'has_password')
        extra_kwargs = {'password': {'write_only': True}}
