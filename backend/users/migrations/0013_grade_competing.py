# Generated by Django 4.2 on 2023-04-30 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_clazz_options_alter_grade_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='competing',
            field=models.BooleanField(default=True, verbose_name='Súťažná?'),
        ),
    ]