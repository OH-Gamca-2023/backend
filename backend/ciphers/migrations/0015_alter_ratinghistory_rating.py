# Generated by Django 4.2.4 on 2023-11-30 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ciphers', '0014_alter_ratinghistory_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratinghistory',
            name='rating',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ciphers.rating'),
        ),
    ]
