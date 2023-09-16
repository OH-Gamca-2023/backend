import random

from django.core.exceptions import ValidationError
from django.db import models
from mdeditor.fields import MDTextField

from backend import settings
from backend.disciplines.models import Discipline
from backend.users.models import Grade


class Tag(models.Model):
    name = models.CharField("Názov", max_length=100)
    special = models.CharField("Špeciálna funkcia", max_length=10, blank=True, null=True,
                               help_text="Používané interne. NEUPRAVUJTE ak neviete čo robíte.")

    def __str__(self):
        return "[" + self.name + "]"

    class Meta:
        verbose_name_plural = 'tagy'
        verbose_name = 'tag'

        permissions = [
            ('add_special_tag', 'Can add special tag'),
            ('change_special_tag', 'Can change special tag'),
            ('delete_special_tag', 'Can delete special tag')
        ]


def gen_id():
    return "".join(random.choices("0123456789abcdef", k=8))


class Post(models.Model):
    id = models.CharField(max_length=15, primary_key=True, unique=True, default=gen_id)

    title = models.CharField("Nadpis", max_length=100)
    content = MDTextField("Obsah", max_length=20000, blank=True, null=True)
    redirect = models.CharField("Presmerovanie", max_length=100, blank=True, null=True,
                                help_text="Presmerovanie na inú stránku. Ak je vyplnené, obsah bude ignorovaný.")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Autor")
    date = models.DateTimeField("Dátum", auto_now_add=True)

    related_disciplines = models.ManyToManyField('disciplines.Discipline', blank=True, related_name='posts_for_discipline',
                                                 verbose_name="Súvisiace disciplíny")
    affected_grades = models.ManyToManyField('users.Grade', blank=True, related_name='posts_for_category',
                                             verbose_name="Ovplyvnené stupne")
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts_for_tag', verbose_name="Tagy")

    @property
    def discipline_categories(self):
        return self.related_disciplines.all().values_list('category', flat=True).distinct()

    discipline_categories.fget.short_description = "Kategórie disciplín"

    def __str__(self):
        if self.author is None:
            return self.title + " (administátor)"
        return self.title + " (" + self.author.username + ")"

    def clean(self):
        if not self.content and not self.redirect:
            raise ValidationError({
                'content': 'Obsah alebo presmerovanie musí byť vyplnené.'
            })

    class Meta:
        verbose_name_plural = 'príspevky'
        verbose_name = 'príspevok'

        permissions = [
            ('change_others_post', 'Can change posts of other users'),
            ('delete_others_post', 'Can delete posts of other users'),
            ('post_as_other', 'Can post as other user')
        ]