import random

from django.core.exceptions import ValidationError
from django.db import models
from mdeditor.fields import MDTextField

from backend import settings


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
    start_time = models.TimeField("Čas začiatku", blank=True, null=True)
    end_time = models.TimeField("Čas konca", blank=True, null=True)
    location = models.CharField("Miesto", max_length=100, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategória")
    target_grades = models.ManyToManyField('users.Grade', blank=True, verbose_name="Cielené stupne",
                                           limit_choices_to={'competing': True})

    primary_organisers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                                related_name="primary_disciplines",
                                                verbose_name="Zodpovedný organizátori",
                                                limit_choices_to={'clazz__grade__is_organiser': True})
    teacher_supervisors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name="Dozorujúci učitelia",
                                                 related_name="disciplines_to_supervise",
                                                 limit_choices_to={'clazz__grade__is_teacher': True})

    date_published = models.BooleanField(default=False, verbose_name="Dátum zverejnený")
    details_published = models.BooleanField(default=False, verbose_name="Detaily zverejnené")
    results_published = models.BooleanField(default=False, verbose_name="Výsledky zverejnené")

    def clean(self):
        if self.date_published and not self.date:
            raise ValidationError({
                'date_published': f'Dátum musí byť zadaný ak má byť zverejnený.'
            })

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
            ('hide_published', 'Can hide published data'),
            ('modify_people', 'Can modify organisers and supervisors'),
            ('view_hidden', 'Can view disciplines that are not public'),
            ('view_primary_organisers', 'Can view primary organisers'),
            ('view_teacher_supervisors', 'Can view teacher supervisors'),
        ]


class Result(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name="Disciplína")
    name = models.CharField("Názov výsledkovky",
                            max_length=100,
                            blank=True,
                            null=True,
                            help_text="Zobrazí sa ak sú k disciplíne priradené viaceré výsledkovky.")
    grades = models.ManyToManyField('users.Grade', blank=True, verbose_name="Stupne", help_text="Stupne z ktorých triedy sa "
                                                                                        "mali v disciplíne zúčastniť.",
                                    limit_choices_to={'competing': True})

    class Meta:
        verbose_name_plural = 'výsledkovky'
        verbose_name = 'výsledkovka'

    def __str__(self):
        if self.name is not None:
            return self.name + ' (Výsledky)'
        return self.discipline.name + ' (Výsledky)'


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

    clazz = models.ForeignKey('users.Clazz', on_delete=models.CASCADE, verbose_name="Trieda", related_name="placements")
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
