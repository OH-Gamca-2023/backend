from rest_framework import serializers

from backend.data.models import Alert, Setting


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ('id', 'message', 'type', 'created_at', 'lasts_until', 'active')


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('key', 'value')