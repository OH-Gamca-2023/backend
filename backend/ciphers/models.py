from django.db import models

from backend.users.models import Clazz


class Cipher(models.Model):
    name = models.CharField(max_length=100)

    start = models.DateTimeField()
    task_file = models.FileField(upload_to='ciphers/tasks/')  # TODO: Limit to .pdf
    visible = models.BooleanField(default=False)  # TODO: auto update on start

    hint_text = models.CharField(max_length=1000, blank=True, null=True)
    hint_file = models.FileField(upload_to='ciphers/hints/', blank=True, null=True)  # TODO: Limit to .pdf
    # TODO: only one of the two above can be set
    hint_publish_time = models.DateTimeField(blank=True, null=True)
    hint_visible = models.BooleanField(default=False)  # TODO: auto update on hintPublishTime

    correct_answer = models.CharField(max_length=20)  # TODO: ensure this is never sent to the client

    end = models.DateTimeField()
    has_ended = models.BooleanField(default=False)  # TODO: auto update on end


class Submission(models.Model):
    cipher = models.ForeignKey(Cipher, on_delete=models.CASCADE)
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE)

    answer = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    after_hint = models.BooleanField(default=False)

    correct = models.BooleanField(default=False)
