from rest_framework import permissions
from rest_framework.views import APIView

from .backends import CredentialsAuthentication
from .providers import get_oauth_provider
from knox import views as knox_views


class OauthStartView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, service):
        provider = get_oauth_provider(service)
        return provider.begin(request)


class OauthCallbackView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, service):
        provider = get_oauth_provider(service)
        return provider.callback(request)


class OauthVerifyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, service):
        provider = get_oauth_provider(service)
        return provider.verify(request)

class LoginView(knox_views.LoginView):
    authentication_classes = (CredentialsAuthentication,)