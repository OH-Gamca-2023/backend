import json
import re

from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from messages.error import not_authenticated, invalid_method, client_error

from data.permissions import profile_edit_permission
from .serializers import *


class CurrentUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return JsonResponse(serializer.data)

    def post(self, request):
        data = json.loads(request.body)
        # validate that the user is allowed to edit all the fields present in the request
        for field in data:
            if field not in profile_edit_permission[request.user.type()]:
                return client_error(403, 'no_permission.change', field)
            if data[field] == '':
                return client_error(400, 'non_empty', field)

        if 'email' in data and re.match(r'^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$', data['email']) is None:
            return client_error(400, 'invalid', 'email')

        user = User.objects.get(pk=request.user.pk)
        user.first_name = data['first_name'] if 'first_name' in data else user.first_name
        user.last_name = data['last_name'] if 'last_name' in data else user.last_name
        user.email = data['email'] if 'email' in data else user.email
        user.username = data['username'] if 'username' in data else user.username
        user.save()

        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)


class UserPermissionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_authenticated:
            return not_authenticated()
        user_type = request.user.type()

        response = {
            'user_type': user_type,
            'staff': request.user.is_staff,
            'admin': request.user.is_admin,
            'superuser': request.user.is_superuser,
            'permissions': [(perm.content_type.app_label + '.' + perm.codename) for perm in request.user.get_all_permissions()],
            'profile_edit': []
        }

        if user_type in profile_edit_permission:
            response['profile_edit'] = profile_edit_permission[user_type]

        return JsonResponse(response)


class PasswordChangeAPIView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if request.user.has_password():
            return client_error(405, 'custom', 'POST is not allowed if the user already has a password, use PUT instead')

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def put(self, request):
        if not request.user.is_authenticated:
            return not_authenticated()

        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if not request.user.has_password():
            return client_error(405, 'custom', 'PUT is not allowed if the user does not have a password, use POST '
                                               'instead')

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def validate(self, request, data):
        if 'new_password' not in data:
            return client_error(400, 'required', 'New password')
        if request.user.has_password() and 'old_password' not in data:
            return client_error(400, 'required', 'Old password')

        if request.user.has_password() and not request.user.check_password(data['old_password']):
            return client_error(400, 'incorrect', 'Old password')

        if request.user.has_password() and data['new_password'] == data['old_password']:
            return client_error(409, 'not_the_same', 'New password', 'old password')
        if len(data['new_password']) < 8:
            return client_error(409, 'too_short', 'New password', 8)
        if len(data['new_password']) > 128:
            return client_error(409, 'too_long', 'New password', 128)
        if not (any(char.isdigit() for char in data['new_password']) or any(not char.isalnum() for char in data['new_password'])):
            return client_error(409, 'password.no_not_alpha')
        if not any(char.isalpha() for char in data['new_password']):
            return client_error(409, 'password.no_alpha')

        return None


class ClassListAPIView(APIView):
    def get(self, request):
        serializer = ClazzSerializer(Clazz.objects.all(), many=True)

        return JsonResponse(serializer.data, safe=False)


class ClassDetailAPIView(APIView):
    def get(self, request, pk):
        serializer = ClazzSerializer(Clazz.objects.get(pk=pk))

        return JsonResponse(serializer.data, safe=False)


class GradeListAPIView(APIView):
    def get(self, request):
        serializer = GradeSerializer(Grade.objects.all(), many=True)

        return JsonResponse(serializer.data, safe=False)


class GradeDetailAPIView(APIView):
    def get(self, request, pk):
        serializer = GradeSerializer(Grade.objects.get(pk=pk))

        return JsonResponse(serializer.data, safe=False)