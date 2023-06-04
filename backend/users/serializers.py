from rest_framework import serializers

from .models import User, Clazz, Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('id', 'name', 'competing', 'cipher_competing')


class ClazzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clazz
        fields = ('id', 'name', 'grade', 'is_fake')


class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, hide_confidential=False, **kwargs):
        super().__init__(*args, **kwargs)
        if hide_confidential:
            self.fields.pop('microsoft_user')
            self.fields.pop('has_password')
            self.fields.pop('email')
            self.fields.pop('clazz')
            self.fields.pop('phone_number')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'clazz', 'type',
                  'microsoft_user', 'has_password')
        extra_kwargs = {'password': {'write_only': True}}
