# Generated by Django 4.1.7 on 2023-03-16 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_userapitoken_usertoken_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertoken',
            name='last_ip',
        ),
        migrations.RemoveField(
            model_name='usertoken',
            name='last_used',
        ),
        migrations.AddField(
            model_name='usertoken',
            name='invalid',
            field=models.BooleanField(default=False),
        ),
    ]
