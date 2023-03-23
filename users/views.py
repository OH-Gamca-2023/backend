import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from messages.error import not_authenticated, invalid_method, client_error
from users.serializers import *


def current_user(request):
    if not request.user.is_authenticated:
        return not_authenticated()
    user = UserSerializer(request.user)
    return JsonResponse(user.data)


@csrf_exempt
def change_password(request):
    if not request.user.is_authenticated:
        return not_authenticated()
    if request.method != 'POST' and request.method != 'PUT':
        return invalid_method(['POST', 'PUT'])

    if not request.user.is_staff:
        return client_error(403, 'no_permission.change', 'your password')

    data = request.POST if request.method == 'POST' else json.loads(request.body)

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

    request.user.set_password(data['new_password'])
    request.user.save()

    return HttpResponse(status=204)


def classes(request):
    serializer = ClazzSerializer(Clazz.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


def grades(request):
    serializer = GradeSerializer(Grade.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)