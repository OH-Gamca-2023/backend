import random

from django.core.exceptions import ValidationError
from django.db import models

from backend import settings


class Calendar(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    content_type = models.CharField(max_length=255)
    content = models.TextField()
    is_current = models.BooleanField(default=False)
    id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "Calendar: %s [%s]" % (self.key, self.id)

    class Meta:
        default_permissions = ('view',)
        permissions = [
            ('view_all', 'Can view all calendars'),
        ]


def gen_id():
    return "EV" + "".join(random.choices("0123456789abcdef", k=8))


class Event(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=gen_id)
    name = models.CharField("Názov", max_length=100)
    date = models.DateField("Dátum začiatku", blank=False, null=False)
    start_time = models.TimeField("Čas začiatku", blank=False, null=False)
    end_time = models.TimeField("Čas konca", blank=True, null=True)
    location = models.CharField("Miesto", max_length=100, blank=True, null=True)
    category = models.ForeignKey("disciplines.Category", verbose_name="Kategória", on_delete=models.CASCADE)
    only_staff = models.BooleanField("Viditeľné len s dodatočným povolením", default=False)

    def __str__(self):
        return "Event: %s" % self.name


class GenerationEvent(models.Model):
    cause = models.CharField(max_length=255)
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    initiation_time = models.DateTimeField(auto_now_add=True)

    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()

    was_successful = models.BooleanField(default=False)
    result = models.CharField(max_length=255)
    generated_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "GenerationEvent: %s @ %s" % (self.cause, self.initiation_time)

