from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from messages.error import client_error, server_error


def status(request):
    response = {
        "status": "ok",
        "time": datetime.now().isoformat(),
        "token": {
            "present": False
        }
    }

    auth_header = request.headers.get('Authorization')
    if auth_header:
        raw_token = auth_header.split(' ')[1]
        response['token']['present'] = True

        response['token']['found'] = False
        response['token']['valid'] = False
        response['token']['expires'] = None
        response['token']['expired'] = False
        response['token']['user'] = None

    return JsonResponse(response)


def home(request):
    return HttpResponse(status=302, headers={'Location': '/admin/'})


def handler404(request, exception):
    return client_error(404, "endpoint_not_found")


def handler500(request):
    return server_error(500, "internal_unknown")
