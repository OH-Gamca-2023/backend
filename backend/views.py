from django.http import JsonResponse
from django.utils import timezone


def status(request):
    return JsonResponse({'status': 'ok'})
