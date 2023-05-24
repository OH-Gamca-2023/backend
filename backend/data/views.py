from rest_framework import viewsets

from data.models import Alert, Setting
from data.serializers import AlertSerializer, SettingSerializer


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.filter(show_on_site=True, active=True)
    serializer_class = AlertSerializer


class SettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setting.objects.filter(exposed=True)
    serializer_class = SettingSerializer
