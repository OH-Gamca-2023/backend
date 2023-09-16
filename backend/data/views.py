from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View
from rest_framework import viewsets

from backend.data.models import Alert, Setting, Link
from backend.data.serializers import AlertSerializer, SettingSerializer


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.filter(show_on_site=True, active=True, lasts_until__gte=timezone.now())
    serializer_class = AlertSerializer


class SettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setting.objects.filter(exposed=True)
    serializer_class = SettingSerializer


class LinkView(View):
    def get(self, request, key):
        print(key)
        link = Link.get(key, request.user)
        if link:
            return redirect(link, permanent=False)
        else:
            return HttpResponseNotFound()