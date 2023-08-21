# Generated by Django 4.2.1 on 2023-08-21 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_alter_authrestriction_full'),
    ]

    operations = [
        migrations.CreateModel(
            name='HueyTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField()),
                ('name', models.CharField(max_length=300, verbose_name='názov')),
                ('signal', models.CharField(blank=True, choices=[('canceled', 'canceled'), ('complete', 'complete'), ('error', 'error'), ('executing', 'executing'), ('expired', 'expired'), ('locked', 'locked'), ('retrying', 'retrying'), ('revoked', 'revoked'), ('scheduled', 'scheduled'), ('interrupted', 'interrupted')], max_length=20, null=True)),
                ('is_finished', models.BooleanField(verbose_name='je ukončený')),
                ('error', models.TextField(blank=True, null=True, verbose_name='chyba')),
                ('retries_left', models.PositiveIntegerField(blank=True, null=True, verbose_name='ostávajúce opakovania')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Huey úloha',
                'verbose_name_plural': 'Huey úlohy',
                'ordering': ['-timestamp'],
                'default_permissions': ('view',),
            },
        ),
    ]