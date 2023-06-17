from rest_framework import serializers

from data.permissions import profile_edit_permission
from .models import User, Clazz, Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('id', 'name', 'competing', 'cipher_competing', 'is_organiser', 'is_teacher')


class ClazzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clazz
        fields = ('id', 'name', 'grade', 'is_fake')


class PermissionSerializer(serializers.Serializer):
    staff = serializers.BooleanField()
    teacher = serializers.BooleanField()
    admin = serializers.BooleanField()
    superuser = serializers.BooleanField()
    type = serializers.CharField(max_length=100)
    profile_edit = serializers.ListSerializer(child=serializers.CharField(max_length=100))
    permissions = serializers.ListSerializer(child=serializers.CharField(max_length=100))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = {
            'staff': user.is_staff,
            'teacher': user.clazz.grade.is_teacher,
            'superuser': user.is_superuser,
            'type': user.type(),
            'profile_edit': [],
            'permissions': [(perm.content_type.app_label + '.' + perm.codename) for perm in user.get_all_permissions()],
        }

        if user.type() in profile_edit_permission:
            self.instance['profile_edit'] = profile_edit_permission[user.type()]


class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, hide_personal=False, hide_confidential=False, permissions=False, **kwargs):
        super().__init__(*args, **kwargs)
        if hide_personal:
            self.fields.pop('email')
            self.fields.pop('phone_number')
            self.fields.pop('clazz')
            hide_confidential = True  # hide_confidential is implied by hide_personal

        if hide_confidential:
            self.fields.pop('microsoft_user')
            self.fields.pop('has_password')
            self.fields.pop('individual_cipher_solving')
            permissions = False  # !permissions is implied by hide_confidential

        self.permissions = permissions

    def to_representation(self, instance):
        serialized = super().to_representation(instance)
        if self.permissions:
            serialized['permissions'] = PermissionSerializer(user=instance).data
        return serialized

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'clazz', 'type',
                  'microsoft_user', 'has_password', 'individual_cipher_solving')
        extra_kwargs = {'password': {'write_only': True}}

