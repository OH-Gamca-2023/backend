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

