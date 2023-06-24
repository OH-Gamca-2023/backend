from rest_framework import viewsets

from backend.data.models import Alert, Setting
from backend.data.serializers import AlertSerializer, SettingSerializer


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.filter(show_on_site=True, active=True)
    serializer_class = AlertSerializer


class SettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setting.objects.filter(exposed=True)
    serializer_class = SettingSerializer
