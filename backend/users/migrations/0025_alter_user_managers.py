# Generated by Django 4.2.1 on 2023-06-27 14:46

import backend.users.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_user_managers'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', backend.users.models.CustomUserManager()),
            ],
        ),
    ]