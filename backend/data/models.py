import json
import random

from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import models
from knox.models import AuthToken


class Setting(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=5000)

    exposed = models.BooleanField(default=False, help_text='Whether this setting is exposed to the API.')

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
    def remove(key):
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
                                 help_text='Specific IP address which can bypass this restriction. '
                                           'Multiple can be separated by commas.')
    bypass_staff = models.BooleanField(default=False,
                                       help_text='Whether staff members can bypass this restriction.')
    bypass_superuser = models.BooleanField(default=True,
                                           help_text='Whether superusers can bypass this restriction.')
    bypass_department = models.CharField(max_length=1000, blank=True,
                                         help_text='Specific department which can bypass this restriction. '
                                                   'Multiple departments can be separated by commas.',
                                         default='SextaA,II.A')

    message = models.CharField(max_length=1000, blank=True,
                               help_text='Message to be displayed when this restriction is active.')

    def __str__(self):
        return self.type + (' (enabled)' if self.restricted else ' (disabled)')

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.type == 'login':
            # Log out all users when login restriction is changed (for security reasons)
            Session.objects.all().delete()
            AuthToken.objects.all().delete()

        super().save(force_insert, force_update, using, update_fields)


def gen_id():
    return "".join(random.choices("0123456789abcdef", k=4))


class Alert(models.Model):
    TYPE_CHOICES = (
        ('success', 'Úspešné'),
        ('info', 'Informácia'),
        ('warning', 'Varovanie'),
        ('error', 'Chyba')
    )

    def get_django_level(self):
        if self.type == 'success':
            return messages.SUCCESS
        elif self.type == 'warning':
            return messages.WARNING
        elif self.type == 'error':
            return messages.ERROR
        else:
            return messages.INFO

    id = models.CharField(max_length=15, primary_key=True, unique=True, default=gen_id)

    message = models.CharField(max_length=200)
    type = models.CharField(choices=TYPE_CHOICES)

    show_on_site = models.BooleanField(default=True)
    show_in_admin = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    lasts_until = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.message} ({self.type})'