# Generated by Django 4.2.1 on 2023-05-18 17:53

import ciphers.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciphers', '0004_submission_submitted_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cipher',
            name='has_ended',
        ),
        migrations.RemoveField(
            model_name='cipher',
            name='hint_visible',
        ),
        migrations.RemoveField(
            model_name='cipher',
            name='visible',
        ),
        migrations.AlterField(
            model_name='cipher',
            name='task_file',
            field=models.FileField(upload_to=ciphers.models.file_path, validators=[ciphers.models.validate_file]),
        ),
    ]
