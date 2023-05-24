import random

from django.db import models
from mdeditor.fields import MDTextField

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

    details = MDTextField("Detaily", max_length=8000, blank=True, null=True)

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

    @property
    def is_public(self):
        return self.date_published or self.details_published or self.results_published

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('publish_date', 'Can publish date'),
            ('publish_details', 'Can publish details'),
            ('publish_results', 'Can publish results'),
        ]


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

    def __str__(self):
        if self.name is not None:
            return self.name + ' (Výsledky)'
        return self.discipline.name + ' (Výsledky)'

    @property
    def markdown(self):
        md = ""
        if self.name is not None:
            md += f"#### {self.name}  \n"

        placements = self.placements.all()
        max_place = max([p.place for p in placements])
        for place in range(1, max_place + 1):
            md += f"**{place}. miesto** - "
            l = []
            for placement in placements.filter(place=place):
                l.append(f"{placement.clazz.name}")
            md += ", ".join(l) + "  \n"

        if len(placements.filter(place=-1)) > 0:
            md += f"\n_Nezúčastnili sa: "
            l = []
            for placement in placements.filter(place=-1):
                l.append(f"{placement.clazz.name}")
            md += ", ".join(l) + "_  \n\n"

        return md


class PlacementManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().annotate(
            p=models.Case(
                models.When(place__gt=0, then=True),
                default=False,
                output_field=models.BooleanField()
            )
        ).order_by('-p', 'place')


class Placement(models.Model):
    objects = PlacementManager()
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name="Výsledkovka", related_name="placements")

    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, verbose_name="Trieda", related_name="placements")
    place = models.SmallIntegerField("Pozícia", default=-1, null=False, blank=False)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.place < 1:
            self.place = -1
        super().save(force_insert, force_update, using, update_fields)

    @property
    def participated(self):
        return self.place > 0

    class Meta:
        verbose_name_plural = 'umiestnenia'
        verbose_name = 'umiestnenie'
