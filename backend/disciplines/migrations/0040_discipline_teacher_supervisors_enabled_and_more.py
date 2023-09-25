# Generated by Django 4.2.4 on 2023-09-25 08:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disciplines', '0039_discipline_result_details_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='teacher_supervisors_enabled',
            field=models.BooleanField(default=False, verbose_name='Povoliť prihlasovanie učiteľov do poroty'),
        ),
        migrations.AlterField(
            model_name='discipline',
            name='teacher_supervisors',
            field=models.ManyToManyField(blank=True, limit_choices_to={'clazz__grade__is_teacher': True}, related_name='disciplines_to_supervise', to=settings.AUTH_USER_MODEL, verbose_name='Učitelia v porote'),
        ),
    ]
