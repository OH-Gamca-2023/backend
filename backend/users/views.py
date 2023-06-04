import json
import re

from django.http import JsonResponse, HttpResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from data.permissions import profile_edit_permission
from .serializers import *
from backend.utils import ViewModelPermissions


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return JsonResponse(serializer.data)

    def post(self, request):
        data = json.loads(request.body)
        # validate that the user is allowed to edit all the fields present in the request
        for field in data:
            if field not in profile_edit_permission[request.user.type()]:
                return JsonResponse({'error': 'You are not allowed to modify ' + field}, status=403)
            if data[field] == '' and field != 'phone_number':
                return JsonResponse({'error': field + ' cannot be empty'}, status=400)

        if 'email' in data and re.match(r'^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$', data['email']) is None:
            return JsonResponse({'error': 'Invalid email'}, status=400)

        user = User.objects.get(pk=request.user.pk)
        user.first_name = data['first_name'] if 'first_name' in data else user.first_name
        user.last_name = data['last_name'] if 'last_name' in data else user.last_name
        user.email = data['email'] if 'email' in data else user.email
        user.username = data['username'] if 'username' in data else user.username
        user.save()

        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)


class CurrentUserPermissionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
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


class PasswordChangeView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if request.user.has_password():
            return JsonResponse({'error': 'POST not allowed for users with password'}, status=405)

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def put(self, request):
        data = json.loads(request.body)

        error = self.validate(request, data)
        if error is not None:
            return error

        if not request.user.has_password():
            return JsonResponse({'error': 'PUT not allowed for users without password'}, status=405)

        request.user.set_password(data['new_password'])
        request.user.save()

        return HttpResponse(status=204)

    def validate(self, request, data):
        if 'new_password' not in data:
            return JsonResponse({'error': 'New password is required'}, status=400)
        if request.user.has_password() and 'old_password' not in data:
            return JsonResponse({'error': 'Old password is required'}, status=400)

        if request.user.has_password() and not request.user.check_password(data['old_password']):
            return JsonResponse({'error': 'Old password is incorrect'}, status=401)

        if request.user.has_password() and data['new_password'] == data['old_password']:
            return JsonResponse({'error': 'New password cannot be the same as the old password'}, status=409)
        if len(data['new_password']) < 8:
            return JsonResponse({'error': 'New password must be at least 8 characters long'}, status=409)
        if len(data['new_password']) > 128:
            return JsonResponse({'error': 'New password cannot be longer than 128 characters'}, status=409)
        if not (any(char.isdigit() for char in data['new_password']) or any(not char.isalnum() for char in data['new_password'])):
            return JsonResponse({'error': 'New password must contain at least one digit or special character'}, status=409)
        if not any(char.isalpha() for char in data['new_password']):
            return JsonResponse({'error': 'New password must contain at least one letter'}, status=409)

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