from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from messages.error import client_error, server_error
from users.models import UserToken


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

        token = UserToken.objects.filter(token=raw_token).first()
        if token:
            response['token']['found'] = True
            response['token']['valid'] = not token.invalid
            response['token']['expires'] = token.expires.isoformat()
            response['token']['expired'] = token.expires < timezone.now()
            if not token.invalid and token.expires > timezone.now():
                response['token']['user'] = {
                    "id": token.user.id,
                    "username": token.user.username,
                    "email": token.user.email,
                    "type": token.user.type(),
                }
        else:
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
