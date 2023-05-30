import hashlib
import os

from django.db import models
from django.utils import timezone

from backend import settings
from users.models import Clazz


def file_path(instance, filename):
    instance.task_file.open()
    fname, ext = os.path.splitext(filename)
    digest = hashlib.sha256(instance.task_file.read()).hexdigest()[:16]
    return f'sifry/zadania/{digest}{ext}'


def validate_file(file):
    if file.size > settings.CIPHERS_MAX_FILE_SIZE:
        raise Exception('File too large.')
    fname, ext = os.path.splitext(file.name)
    if ext not in settings.CIPHERS_ALLOWED_FILE_TYPES:
        raise Exception('Invalid file type.')


class Cipher(models.Model):
    name = models.CharField(max_length=100)

    start = models.DateTimeField()
    task_file = models.FileField(upload_to=file_path, validators=[validate_file])

    submission_delay = models.IntegerField(default=600, help_text='Čas v sekundách, ktorý musí uplynúť pred odoslaním'
                                                                  'ďalšej odpovede. Predvolená hodnota je 600 sekúnd'
                                                                  '(10 minút), odporúčame nemeniť. Pri individuálnom '
                                                                  'riešení je táto hodnota zdvojnásobená.',
                                           verbose_name='Interval medzi odpoveďami')

    hint_text = models.CharField(max_length=1000, blank=True, null=True)
    hint_publish_time = models.DateTimeField(blank=True, null=True)

    correct_answer = models.CharField(max_length=20)

    end = models.DateTimeField()

    @property
    def started(self):
        return self.start < timezone.now()

    @property
    def hint_visible(self):
        if not self.hint_publish_time:
            return False
        return self.hint_publish_time < timezone.now()

    @property
    def has_ended(self):
        return self.end < timezone.now()

    def save(self, *args, **kwargs):
        if self.start and self.end and self.start > self.end:
            raise Exception('Start date must be before end date.')
        elif self.start and self.hint_publish_time and self.start > self.hint_publish_time:
            raise Exception('Start date must be before hint publish date.')
        elif self.hint_publish_time and self.end and self.hint_publish_time > self.end:
            raise Exception('Hint publish date must be before end date.')

        super(Cipher, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def _submission_set(self, target, is_user=False):
        if is_user:
            return self.submission_set.filter(submitted_by=target)
        return self.submission_set.filter(clazz=target)

    def solved_by(self, target, is_user=False):
        return self._submission_set(target, is_user).filter(correct=True).exists()

    def solved_after_hint_by(self, target, is_user=False):
        if self.solved_by(target, is_user):
            return self._submission_set(target, is_user).filter(correct=True).order_by('time').first().after_hint
        return False

    def attempts_by(self, target, is_user=False):
        return self._submission_set(target, is_user).count()


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
        if not self.pk:
            # refuse to create submissions after the cipher has ended
            if self.cipher.has_ended:
                raise Exception('Cipher has ended.')
            # refuse to create submissions before the cipher has started
            if not self.cipher.started:
                raise Exception('Cipher has not started.')
            # refuse to create submissions if the class has already solved the cipher
            if self.cipher.solved_by(self.clazz):
                raise Exception('Class has already solved this cipher.')

            # if creating, set after_hint and correct
            self.correct = self.answer.strip().lower() == self.cipher.correct_answer.strip().lower()
            self.after_hint = self.cipher.hint_visible
        super(Submission, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'[{"✓" if self.correct else "✗"}] {self.clazz.name} - {self.cipher.name}'
