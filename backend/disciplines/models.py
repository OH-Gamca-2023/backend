import random

from django.db import models

from users.models import Grade, Clazz


class Category(models.Model):
    name = models.CharField("Názov", max_length=100)
    calendar_class = models.CharField("CSS trieda", max_length=100, blank=True, null=True,
                                      help_text="CSS trieda, ktorá sa priradí k disciplínam tejto kategórie v "
                                                "kalendári.")

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
    short_name = models.CharField("Krátky názov", max_length=15, blank=True, null=True,
                                    help_text="Zobrazí sa v kalendári. Maximálna dĺžka ktorá sa v kalebdári "
                                                "správne zobrazí je 15 znakov. V prípade viac ako 3 disciplín "
                                                "v jednom dni odporúčame maximálne 7 znakov.")

    details = models.TextField("Detaily", blank=True, null=True)

    date = models.DateField("Dátum", blank=True, null=True)
    time = models.TimeField("Čas", blank=True, null=True)
    location = models.CharField("Miesto", max_length=100, blank=True, null=True)
    volatile_date = models.BooleanField("Neurčitý dátum",
                                        default=False,
                                        help_text="Ak je zaškrtnuté, zobrazí sa varovanie, že dátum sa ešte môže "
                                                  "zmeniť.")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategória")
    target_grades = models.ManyToManyField(Grade, blank=True, verbose_name="Cielené stupne",
                                           limit_choices_to={'competing': True})

    date_published = models.BooleanField(default=False, verbose_name="Dátum zverejnený")
    details_published = models.BooleanField(default=False, verbose_name="Detaily zverejnené")
    results_published = models.BooleanField(default=False, verbose_name="Výsledky zverejnené")

    details_post = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    results_post = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

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
                                                                                        "mali v disciplíne zúčastniť.",
                                    limit_choices_to={'competing': True})

    class Meta:
        verbose_name_plural = 'výsledkovky'
        verbose_name = 'výsledkovka'


class Placement(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name="Výsledkovka", related_name="placements")

    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, verbose_name="Trieda", related_name="placements")
    place = models.SmallIntegerField("Pozícia", default=-1)
    # TODO: indexujeme od 1, -1 znamená, že sa nezúčastnili

    class Meta:
        verbose_name_plural = 'umiestnenia'
        verbose_name = 'umiestnenie'
