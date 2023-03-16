from django.contrib.auth import login
from django.http import HttpResponse
from django.utils import timezone

from users.models import UserToken


class HeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == 'OPTIONS':
            response = HttpResponse()
            response.status_code = 200

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'

        return response


class BearerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            raw_token = auth_header.split(' ')[1]

            token = UserToken.objects.filter(token=raw_token, invalid=False, expires__gt=timezone.now()).first()
            if token:
                login(request, token.user)
            else:
                request.user = None
        else:
            request.user = None

        response = self.get_response(request)
        return response
