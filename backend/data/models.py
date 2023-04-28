import json

from django.db import models


class Setting(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=5000)

    def __str__(self):
        return f'{self.key} = {self.value}'

    @staticmethod
    def get(key, default=None):
        try:
            return Setting.objects.get(key=key).value
        except Setting.DoesNotExist:
            if default is None:
                raise
            return default

    @staticmethod
    def set(key, value):
        Setting.objects.update_or_create(key=key, defaults={'value': value})

    @staticmethod
    def delete(key):
        Setting.objects.filter(key=key).delete()

    @staticmethod
    def get_bool(key, default=None):
        return Setting.get(key, default) == '1'

    @staticmethod
    def set_bool(key, value):
        Setting.set(key, '1' if value else '0')

    @staticmethod
    def get_int(key, default=None):
        return int(Setting.get(key, default))

    @staticmethod
    def set_int(key, value):
        Setting.set(key, str(value))

    @staticmethod
    def get_float(key, default=None):
        return float(Setting.get(key, default))

    @staticmethod
    def set_float(key, value):
        Setting.set(key, str(value))

    @staticmethod
    def get_object(key, default=None):
        return eval(Setting.get(key, json.dumps(default)))

    @staticmethod
    def set_object(key, value):
        Setting.set(key, json.dumps(value))


class AuthRestriction(models.Model):
    type = models.CharField(choices=(
        ('login', 'Prihlasovanie'),
        ('register', 'Registrácia'),
    ), max_length=10, primary_key=True)
    restricted = models.BooleanField(default=True, help_text='Whether this restriction is enabled.')

    bypass_ip = models.CharField(max_length=1000, blank=True,
                                 help_text='Specific IP address or a IP range which can bypass this restriction. '
                                           'Multiple ranges can be separated by commas.')
    bypass_staff = models.BooleanField(default=False,
                                       help_text='Whether staff members can bypass this restriction.')
    bypass_admin = models.BooleanField(default=True,
                                       help_text='Whether administrators can bypass this restriction.')
    bypass_superuser = models.BooleanField(default=True,
                                           help_text='Whether superusers can bypass this restriction.')
    bypass_department = models.CharField(max_length=1000, blank=True,
                                         help_text='Specific department which can bypass this restriction. '
                                                   'Multiple departments can be separated by commas.',
                                         default='SextaA,II.A')

    def __str__(self):
        return self.type + (' (enabled)' if self.restricted else ' (disabled)')

