from django.db import models

from users.models import Grade, Clazz


class Tag(models.Model):
    name = models.CharField(max_length=100)


class Category(models.Model):
    name = models.CharField(max_length=100)


class Discipline(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    tags = models.ManyToManyField(Tag, blank=True)

    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    target_grades = models.ManyToManyField(Grade, blank=True)

    date_published = models.BooleanField(default=False)
    description_published = models.BooleanField(default=False)


class Results(models.Model):
    discipline = models.OneToOneField(Discipline, on_delete=models.CASCADE)
    placements = models.ManyToManyField(Clazz, through='Placement')


class Placement(models.Model):
    results = models.ForeignKey(Results, on_delete=models.CASCADE)
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE)
    place = models.PositiveSmallIntegerField(default=-1)  # indexujeme od 1, -1 znamená, že sa nezúčastnili
