from django.http import JsonResponse

from users.serializers import *


def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=401)
    user = UserSerializer(request.user)
    return JsonResponse(user.data)


def classes(request):
    serializer = ClazzSerializer(Clazz.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


def grades(request):
    serializer = GradeSerializer(Grade.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)