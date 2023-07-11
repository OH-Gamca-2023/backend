from rest_framework import permissions
from rest_framework.views import APIView
from .providers import get_oauth_provider


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