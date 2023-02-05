from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Clazz(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_fake = models.BooleanField(default=False)


class User(AbstractUser):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)

    oauth_token = models.CharField(max_length=150, null=True, blank=True)
    oauth_refresh_token = models.CharField(max_length=150, null=True, blank=True)
