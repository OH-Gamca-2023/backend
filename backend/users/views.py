import json
import re

from django.http import  HttpResponse
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from backend.users.utils import ViewModelPermissions


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user, permissions=True)
        return Response(serializer.data)

    def post(self, request):
        data = json.loads(request.body)
        profile_edit_permission = ProfileEditPermissions.get(request.user)
        # validate that the user is allowed to edit all the fields present in the request
        not_allowed = [field for field in data if not getattr(profile_edit_permission, field, False)]
        if len(not_allowed) > 0:
            return Response({'detail': 'You are not allowed to edit these fields', 'fields': not_allowed}, status=403)
        non_empty = [field for field in data if data[field] == '' and field not in ['phone_number', 'discord_id']]
        if len(non_empty) > 0:
            return Response({'detail': 'These fields cannot be empty', 'fields': non_empty}, status=400)

        if 'email' in data and re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,"
                                        r"61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
                                        data['email']) is None:
            return Response({'detail': 'Invalid email', 'field': ['email']}, status=400)

        phone = PhoneNumber.from_string(data['phone_number']) if 'phone_number' in data else None
        if phone is not None and not phone.is_valid() and phone != '':
            return Response({'detail': 'Invalid phone number', 'field': ['phone_number']}, status=400)

        user = User.objects.get(pk=request.user.pk)
        user.first_name = data['first_name'] if 'first_name' in data else user.first_name
        user.last_name = data['last_name'] if 'last_name' in data else user.last_name
        user.email = data['email'] if 'email' in data else user.email
        user.username = data['username'] if 'username' in data else user.username
        user.phone_number = None if phone == '' else (phone if phone is not None else user.phone_number)
        user.discord_id = data['discord_id'] if 'discord_id' in data else user.discord_id
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)


class CurrentUserPermissionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = PermissionSerializer(user=request.user)
        return Response(serializer.data)


class PasswordChangeView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if request.user.has_password():
            return Response({'detail': 'POST not allowed for users with password'}, status=405)

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def put(self, request):
        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if not request.user.has_password():
            return Response({'detail': 'PUT not allowed for users without password'}, status=405)

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def validate(self, request, data):
        if 'new_password' not in data:
            return Response({'detail': 'New password is required'}, status=400)
        if request.user.has_password() and 'old_password' not in data:
            return Response({'detail': 'Old password is required'}, status=400)

        if request.user.has_password() and not request.user.check_password(data['old_password']):
            return Response({'detail': 'Old password is incorrect'}, status=401)

        if request.user.has_password() and data['new_password'] == data['old_password']:
            return Response({'detail': 'New password cannot be the same as the old password'}, status=409)
        if len(data['new_password']) < 8:
            return Response({'detail': 'New password must be at least 8 characters long'}, status=409)
        if len(data['new_password']) > 128:
            return Response({'detail': 'New password cannot be longer than 128 characters'}, status=409)
        if not (any(char.isdigit() for char in data['new_password']) or any(not char.isalnum() for char in data['new_password'])):
            return Response({'detail': 'New password must contain at least one digit or special character'}, status=409)
        if not any(char.isalpha() for char in data['new_password']):
            return Response({'detail': 'New password must contain at least one letter'}, status=409)

        return None


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (ViewModelPermissions,)


class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    model = Clazz
    serializer_class = ClazzSerializer
    queryset = Clazz.objects.all()


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    model = Grade
    serializer_class = GradeSerializer
    queryset = Grade.objects.all()
