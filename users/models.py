import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Grade(models.Model):
    grade_options = (
        ('2. Stupeň', '2. Stupeň'),
        ('3. Stupeň', '3. Stupeň'),
        ('Organizátori', 'Organizátori'),
        ('Učitelia', 'Učitelia'),
    )
    name = models.CharField(max_length=100, choices=grade_options, unique=True)

    class Meta:
        verbose_name_plural = 'grades'
        verbose_name = 'grade'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        raise Exception('Grade objects cannot be deleted.')


@receiver(post_save, sender=Grade)
def create_grades(sender, instance, created, **kwargs):
    if not created:
        return
    for name in Grade.grade_options:
        Grade.objects.get_or_create(name=name[0])


class Clazz(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    is_fake = models.BooleanField(default=False)
    microsoft_department = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'classes'
        verbose_name = 'class'

    def __str__(self):
        return self.name


class MicrosoftUser(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    mail = models.CharField(max_length=150)

    display_name = models.CharField(max_length=150)
    given_name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)

    job_title = models.CharField(max_length=150)
    office_location = models.CharField(max_length=150)
    department = models.CharField(max_length=150)

    def get_clazz(self):
        return Clazz.objects.filter(microsoft_department=self.department).first()

    def __str__(self):
        return self.display_name + ' (' + self.id + ')'


class User(AbstractUser):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)

    microsoft_user = models.OneToOneField(MicrosoftUser, on_delete=models.CASCADE, null=True, blank=True)

    def type(self):
        if self.is_superuser:
            return 'admin'
        elif self.clazz.grade.name == 'Organizátori':
            return 'organizer'
        elif self.clazz.grade.name == 'Učitelia':
            return 'teacher'
        else:
            return 'student'


class UserToken(models.Model):
    token = models.CharField(max_length=150, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    invalid = models.BooleanField(default=False)

    def token_censored(self):
        return re.sub(r'(?<=.{7}).(?=.{7})', '*', self.token)

    def is_expired(self):
        return timezone.now() > self.expires

    def __str__(self):
        return self.user.username + ' - ' + self.token_censored() + (
            '(invalid)' if self.invalid else ('(expired)' if self.is_expired() else ''))
