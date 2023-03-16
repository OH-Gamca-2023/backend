from django.contrib.auth.models import AbstractUser
from django.db import models


class Grade(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'grades'
        verbose_name = 'grade'

    def __str__(self):
        return self.name


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