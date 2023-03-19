import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.serializers import *


def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=401)
    user = UserSerializer(request.user)
    return JsonResponse(user.data)


@csrf_exempt
def change_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=401)
    if request.method != 'POST' and request.method != 'PUT':
        return JsonResponse({'error': 'only POST and PUT are allowed'}, status=405)

    data = request.POST if request.method == 'POST' else json.loads(request.body)

    if 'new_password' not in data:
        return JsonResponse({'error': 'new_password is required'}, status=400)
    if request.user.has_password() and 'old_password' not in data:
        return JsonResponse({'error': 'old_password is required when user has password'}, status=400)

    if request.user.has_password() and not request.user.check_password(data['old_password']):
        return JsonResponse({'error': 'old_password is incorrect'}, status=403)

    if request.user.has_password() and data['new_password'] == data['old_password']:
        return JsonResponse({'error': 'new_password must be different from old_password'}, status=400)
    if len(data['new_password']) < 8:
        return JsonResponse({'error': 'new_password must be at least 8 characters long'}, status=400)
    if not (any(char.isdigit() for char in data['new_password']) and any(not char.isalnum() for char in data['new_password'])):
        return JsonResponse({'error': 'new_password must contain at least one number or special character'}, status=400)
    if not any(char.isalpha() for char in data['new_password']):
        return JsonResponse({'error': 'new_password must contain at least one letter'}, status=400)

    request.user.set_password(data['new_password'])
    request.user.save()

    return JsonResponse({'success': True}, status=200)


def classes(request):
    serializer = ClazzSerializer(Clazz.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


def grades(request):
    serializer = GradeSerializer(Grade.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)