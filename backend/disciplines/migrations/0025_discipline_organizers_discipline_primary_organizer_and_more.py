# Generated by Django 4.2.1 on 2023-06-04 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disciplines', '0024_alter_placement_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='organizers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'is_staff': True}, related_name='organized_disciplines', to=settings.AUTH_USER_MODEL, verbose_name='Organizátori'),
        ),
        migrations.AddField(
            model_name='discipline',
            name='primary_organizer',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_disciplines', to=settings.AUTH_USER_MODEL, verbose_name='Zodpovedný organizátor'),
        ),
        migrations.AddField(
            model_name='discipline',
            name='teacher_oversight',
            field=models.ManyToManyField(blank=True, limit_choices_to={'grade__is_teacher': True}, related_name='disciplines_to_supervise', to=settings.AUTH_USER_MODEL, verbose_name='Dozorujúci učitelia'),
        ),
    ]
