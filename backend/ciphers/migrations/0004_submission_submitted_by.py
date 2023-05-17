# Generated by Django 4.2 on 2023-05-17 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ciphers', '0003_remove_cipher_hint_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='submitted_by',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
