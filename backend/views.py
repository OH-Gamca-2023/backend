from django.http import JsonResponse, HttpResponse
from django.utils import timezone


def status(request):
    return JsonResponse({'status': 'ok'})


def home(request):
    return HttpResponse(status=302, headers={'Location': '/admin/'})