# Generated by Django 4.2.1 on 2023-07-09 11:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disciplines', '0031_alter_discipline_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='primary_organisers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'clazz__grade__is_organiser': True}, related_name='primary_disciplines', to=settings.AUTH_USER_MODEL, verbose_name='Zodpovedný organizátori'),
        ),
    ]
