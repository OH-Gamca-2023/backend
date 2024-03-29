# Generated by Django 4.2 on 2023-04-28 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthRestrictions',
            fields=[
                ('type', models.CharField(choices=[('login', 'Prihlasovanie'), ('register', 'Registrácia')], max_length=10, primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(default=True)),
                ('bypass_ip', models.CharField(blank=True, help_text='Specific IP address or a IP range which can bypass this restriction. Multiple ranges can be separated by commas.', max_length=1000)),
                ('bypass_staff', models.BooleanField(default=False, help_text='Whether staff members can bypass this restriction.')),
                ('bypass_admin', models.BooleanField(default=True, help_text='Whether administrators can bypass this restriction.')),
                ('bypass_superuser', models.BooleanField(default=True, help_text='Whether superusers can bypass this restriction.')),
                ('bypass_department', models.CharField(blank=True, default='SextaA,II.A', help_text='Specific department which can bypass this restriction. Multiple departments can be separated by commas.', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('key', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=5000)),
            ],
        ),
    ]
