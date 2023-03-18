from django.db import models

from backend import settings
from disciplines.models import Discipline, Tag
from users.models import Grade


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    date = models.DateTimeField(auto_now_add=True)

    related_disciplines = models.ManyToManyField(Discipline, blank=True, related_name='posts_for_discipline')
    affected_grades = models.ManyToManyField(Grade, blank=True, related_name='posts_for_category')
    tags = models.ManyToManyField(Tag, blank=True)

    disable_comments = models.BooleanField(default=False)

    def discipline_categories(self):
        return self.related_disciplines.all().values_list('category', flat=True).distinct()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
