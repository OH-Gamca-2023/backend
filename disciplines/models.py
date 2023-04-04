import random

from django.db import models

from users.models import Grade, Clazz


class Tag(models.Model):
    name = models.CharField("Názov", max_length=100)

    def __str__(self):
        return "[" + self.name + "]"

    class Meta:
        verbose_name_plural = 'tagy'
        verbose_name = 'tag'


class Category(models.Model):
    name = models.CharField("Názov", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'kategórie'
        verbose_name = 'kategória'


def gen_id():
    return "".join(random.choices("0123456789abcdef", k=8))


class Discipline(models.Model):
    id = models.CharField(max_length=15, primary_key=True, unique=True, default=gen_id)

    name = models.CharField("Názov", max_length=100)
    details = models.TextField("Detaily", blank=True, null=True)

    date = models.DateField("Dátum", blank=True, null=True)
    time = models.TimeField("Čas", blank=True, null=True)
    location = models.CharField("Miesto", max_length=100, blank=True, null=True)
    volatile_date = models.BooleanField("Neurčitý dátum",
                                        default=False,
                                        help_text="Ak je zaškrtnuté, zobrazí sa varovanie, že dátum sa ešte môže "
                                                  "zmeniť.")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategória")
    target_grades = models.ManyToManyField(Grade, blank=True, verbose_name="Cielené stupne")

    date_published = models.BooleanField(default=False)
    description_published = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Result(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name="Disciplína")
    name = models.CharField("Názov výsledkovky",
                            max_length=100,
                            blank=True,
                            null=True,
                            help_text="Zobrazí sa ak sú k disciplíne priradené viaceré výsledkovky.")
    grades = models.ManyToManyField(Grade, blank=True, verbose_name="Stupne", help_text="Stupne z ktorých triedy sa "
                                                                                        "mali v disciplíne zúčastniť.")
    placements = models.ManyToManyField(Clazz, through='Placement', verbose_name="Umiestnenia")
    # TODO: Malo by sa predvolene naplniť triedami, z vybraných stupňov s hodnotou -1 (nezúčastnili sa)

    class Meta:
        verbose_name_plural = 'výsledkovky'
        verbose_name = 'výsledkovka'


class Placement(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name="Výsledkovka")
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, verbose_name="Trieda")
    place = models.PositiveSmallIntegerField("Pozícia", default=-1)
    # TODO: indexujeme od 1, -1 znamená, že sa nezúčastnili

    class Meta:
        verbose_name_plural = 'umiestnenia'
        verbose_name = 'umiestnenie'
