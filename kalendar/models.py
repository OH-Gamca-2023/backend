from django.db import models

from backend import settings


class Calendar(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    content_type = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return "Calendar: %s" % self.key


class GenerationEvent(models.Model):
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    initiation_time = models.DateTimeField(auto_now_add=True)
    initiation_reason = models.CharField(max_length=255)

    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()

    result = models.CharField(max_length=255)

    @property
    def requests(self):
        return GenerationRequest.objects.filter(fulfill_event=self)


class GenerationRequest(models.Model):
    cause = models.CharField(max_length=255)
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(auto_now_add=True)

    fulfilled = models.BooleanField(default=False)
    fulfill_event = models.ForeignKey(GenerationEvent, on_delete=models.SET_NULL, null=True, related_name='requests')

    class Meta:
        ordering = ['-time']
