# Generated by Django 4.2.1 on 2023-06-04 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_grade_is_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='is_organizer',
            field=models.BooleanField(default=False, verbose_name='Je organizátorská?'),
        ),
    ]