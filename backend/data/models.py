import json
import random

from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import models
from knox.models import AuthToken

from huey.signals import SIGNAL_CANCELED, SIGNAL_COMPLETE, SIGNAL_ERROR, \
    SIGNAL_EXECUTING, SIGNAL_EXPIRED, SIGNAL_LOCKED, SIGNAL_RETRYING, \
    SIGNAL_REVOKED, SIGNAL_SCHEDULED, SIGNAL_INTERRUPTED

SIGNAL_CHOICES = [
    (SIGNAL_CANCELED, SIGNAL_CANCELED),
    (SIGNAL_COMPLETE, SIGNAL_COMPLETE),
    (SIGNAL_ERROR, SIGNAL_ERROR),
    (SIGNAL_EXECUTING, SIGNAL_EXECUTING),
    (SIGNAL_EXPIRED, SIGNAL_EXPIRED),
    (SIGNAL_LOCKED, SIGNAL_LOCKED),
    (SIGNAL_RETRYING, SIGNAL_RETRYING),
    (SIGNAL_REVOKED, SIGNAL_REVOKED),
    (SIGNAL_SCHEDULED, SIGNAL_SCHEDULED),
    (SIGNAL_INTERRUPTED, SIGNAL_INTERRUPTED)
]


class HueyTask(models.Model):
    uuid = models.UUIDField()
    name = models.CharField(max_length=300, verbose_name='názov')  # snad dlhsie nazvy nebudu
    signal = models.CharField(max_length=20, choices=SIGNAL_CHOICES, null=True, blank=True)
    is_finished = models.BooleanField(verbose_name='je ukončený')

    error = models.TextField(null=True, blank=True, verbose_name='chyba')
    retries_left = models.PositiveIntegerField(null=True, blank=True, verbose_name='ostávajúce opakovania')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Huey úloha'
        verbose_name_plural = 'Huey úlohy'
        default_permissions = ('view',)
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.id}: {self.name} - {self.uuid}'


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

    full = models.BooleanField(default=False, help_text='Whether this restriction applies to all users. '
                                                        'This setting effectively disables all bypasses.')

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


class ProfileEditPermissions(models.Model):
    user_type = models.CharField(max_length=20, primary_key=True)

    username = models.BooleanField(default=False)
    first_name = models.BooleanField(default=False)
    last_name = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    phone_number = models.BooleanField(default=False)
    discord_id = models.BooleanField(default=False)
    password = models.BooleanField(default=False)

    @staticmethod
    def get(user):
        type = user.type()
        return ProfileEditPermissions.objects.get_or_create(user_type=type)[0]


class Link(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    target = models.CharField(max_length=500, blank=True, null=True)

    requires_login = models.BooleanField(default=False)
    requires_staff = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.key} -> {self.target[:30]}{"..." if len(self.target) > 30 else ""}'

    def clean(self):
        if self.requires_staff and not self.requires_login:
            raise ValidationError({'requires_staff': 'Link cannot require staff without requiring login.'})
        if self.class_targets.count() > 0 and not self.requires_login:
            raise ValidationError({'requires_login': 'Link cannot have class targets without requiring login.'})
        if self.class_targets.count() == 0 and not self.target:
            raise ValidationError({'target': 'Link must have either class targets or a target.'})

    @staticmethod
    def get(key, user):
        try:
            obj = Link.objects.get(key=key)
            if obj.requires_login and not user.is_authenticated:
                return None
            if obj.requires_staff and not user.is_staff:
                return None

            if obj.class_targets.count() > 0 and user.is_authenticated:
                for ct in obj.class_targets.all():
                    if user.clazz == ct.clazz:
                        return ct.target

                if obj.target:
                    return obj.target
            else:
                return obj.target

            return None
        except Link.DoesNotExist:
            return None


class LinkClassTarget(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='class_targets')
    clazz = models.ForeignKey('users.Clazz', on_delete=models.CASCADE)
    target = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.link.key} [{self.clazz.name}] -> {self.target[:30]}{"..." if len(self.target) > 30 else ""}'

    class Meta:
        unique_together = ('link', 'clazz')
        verbose_name = 'link pre triedu'
        verbose_name_plural = 'linky pre triedy'
