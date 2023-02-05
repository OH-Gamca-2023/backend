from django.db import models

from backend.disciplines.models import Discipline, Tag
from backend.users.models import Category


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    related_disciplines = models.ManyToManyField(Discipline, blank=True)
    affected_categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    disable_comments = models.BooleanField(default=False)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
