# Generated by Django 4.2.1 on 2023-06-04 08:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disciplines', '0025_discipline_organizers_discipline_primary_organizer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='teacher_oversight',
            field=models.ManyToManyField(blank=True, limit_choices_to={'clazz__grade__is_teacher': True}, related_name='disciplines_to_supervise', to=settings.AUTH_USER_MODEL, verbose_name='Dozorujúci učitelia'),
        ),
    ]
