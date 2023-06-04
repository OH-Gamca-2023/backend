# Generated by Django 4.2.1 on 2023-06-02 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_clazz_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='individual_cipher_solving',
            field=models.BooleanField(default=False, help_text='Používateľ môže riešiť šifrovačku individuálne, bez priradenia do triedy. Ak trieda používateľa súťaží v online šifrovačke, táto možnosť nemá žiadny efekt.', verbose_name='Môže riešiť šifrovačku individuálne'),
        ),
    ]