from django.db import models
from django.utils import timezone

from backend import settings
from users.models import Clazz


class Cipher(models.Model):
    name = models.CharField(max_length=100)

    start = models.DateTimeField()
    task_file = models.FileField(upload_to='ciphers/tasks/')  # TODO: Limit to .pdf
    visible = models.BooleanField(default=False)  # TODO: auto update on start

    hint_text = models.CharField(max_length=1000, blank=True, null=True)
    hint_publish_time = models.DateTimeField(blank=True, null=True)
    hint_visible = models.BooleanField(default=False)  # TODO: auto update on hintPublishTime

    correct_answer = models.CharField(max_length=20)  # TODO: ensure this is never sent to the client

    end = models.DateTimeField()
    has_ended = models.BooleanField(default=False)  # TODO: auto update on end

    def save(self, *args, **kwargs):
        if self.start and self.end and self.start > self.end:
            raise Exception('Start date must be before end date.')
        elif self.start and self.hint_publish_time and self.start > self.hint_publish_time:
            raise Exception('Start date must be before hint publish date.')
        elif self.hint_publish_time and self.end and self.hint_publish_time > self.end:
            raise Exception('Hint publish date must be before end date.')

        if self.start and self.start < timezone.now():
            self.visible = True
        if self.hint_publish_time and self.hint_publish_time < timezone.now():
            self.hint_visible = True
        if self.end and self.end < timezone.now():
            self.has_ended = True
        super(Cipher, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Submission(models.Model):
    cipher = models.ForeignKey(Cipher, on_delete=models.CASCADE)
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    answer = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    after_hint = models.BooleanField(default=False)

    correct = models.BooleanField(default=False)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.correct = self.answer.strip().lower() == self.cipher.correct_answer.strip().lower()
        # if creating, set after_hint
        if not self.pk:
            self.after_hint = self.cipher.hint_visible
        super(Submission, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'[{"✓" if self.correct else "✗"}] {self.clazz.name} - {self.cipher.name}'