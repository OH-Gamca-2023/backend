# Generated by Django 4.2.4 on 2023-08-30 18:09

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('disciplines', '0035_category_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='details',
            field=mdeditor.fields.MDTextField(blank=True, max_length=20000, null=True, verbose_name='Detaily'),
        ),
    ]