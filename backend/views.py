from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from messages.error import client_error, server_error


def status(request):
    return JsonResponse({'status': 'ok'})


def home(request):
    return HttpResponse(status=302, headers={'Location': '/admin/'})


def handler404(request, exception):
    return client_error(404, "endpoint_not_found")


def handler500(request):
    return server_error(500, "internal_unknown")
