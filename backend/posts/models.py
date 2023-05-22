import random

from django.db import models
from mdeditor.fields import MDTextField

from backend import settings
from disciplines.models import Discipline
from users.models import Grade


class Tag(models.Model):
    name = models.CharField("Názov", max_length=100)
    special = models.CharField("Špeciálna funkcia", max_length=10, blank=True, null=True,
                               help_text="Používané interne. NEUPRAVUJTE ak neviete čo robíte.")

    def __str__(self):
        return "[" + self.name + "]"

    class Meta:
        verbose_name_plural = 'tagy'
        verbose_name = 'tag'

    def delete(self, using=None, keep_parents=False):
        if self.special is not None:
            raise Exception("Cannot delete special tag.")
        super().delete(using, keep_parents)


def gen_id():
    return "".join(random.choices("0123456789abcdef", k=8))


class Post(models.Model):
    id = models.CharField(max_length=15, primary_key=True, unique=True, default=gen_id)

    title = models.CharField("Nadpis", max_length=100)
    content = MDTextField("Obsah", max_length=10000)
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
