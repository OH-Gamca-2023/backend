from django.db import models

from backend.backend import settings
from backend.disciplines.models import Discipline, Tag
from backend.users.models import Grade


class Post(models.Model):
    title = models.CharField("Nadpis", max_length=100)
    content = models.CharField("Obsah", max_length=10000, help_text="Obsah príspevku bude prehnaný cez Markdown.")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Autor")
    date = models.DateTimeField("Dátum", auto_now_add=True)

    related_disciplines = models.ManyToManyField(Discipline, blank=True, related_name='posts_for_discipline',
                                                 verbose_name="Súvisiace disciplíny")
    affected_grades = models.ManyToManyField(Grade, blank=True, related_name='posts_for_category',
                                             verbose_name="Ovplyvnené stupne")
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts_for_tag', verbose_name="Tagy")

    disable_comments = models.BooleanField("Vypnuté komentáre", default=False)

    @property
    def discipline_categories(self):
        return self.related_disciplines.all().values_list('category', flat=True).distinct()
    discipline_categories.fget.short_description = "Kategórie disciplín"

    def __str__(self):
        if self.author is None:
            return self.title + " (administátor)"
        return self.title + " (" + self.author.username + ")"

    class Meta:
        verbose_name_plural = 'príspevky'
        verbose_name = 'príspevok'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Príspevok")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.SET_NULL, null=True, blank=True, related_name='comments', verbose_name="Autor")
    content = models.CharField("Obsah", max_length=10000, help_text="Ak je autor príspevku organizátor, obsah bude "
                                                                    "prehnaný cez Markdown.")
    date = models.DateTimeField("Dátum", auto_now_add=True)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="Rodičovský komentár")

    def __str__(self):
        if self.author is None:
            return "Komentár od administátora"
        return "Komentár od " + self.author.username

    class Meta:
        verbose_name_plural = 'komentáre'
        verbose_name = 'komentár'
