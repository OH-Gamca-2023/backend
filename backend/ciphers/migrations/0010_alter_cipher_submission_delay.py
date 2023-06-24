# Generated by Django 4.2.1 on 2023-06-02 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciphers', '0009_remove_cipher_ignore_whitespace_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cipher',
            name='submission_delay',
            field=models.IntegerField(default=600, help_text='Čas v sekundách, ktorý musí uplynúť pred odoslaním ďalšej odpovede. Predvolená hodnota je 600 sekúnd(10 minút), odporúčame nemeniť. Pri individuálnom riešení je táto hodnota zdvojnásobená.', verbose_name='Interval medzi odpoveďami'),
        ),
    ]
