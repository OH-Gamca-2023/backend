# Generated by Django 4.2 on 2023-04-28 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuthRestrictions',
            new_name='AuthRestriction',
        ),
    ]