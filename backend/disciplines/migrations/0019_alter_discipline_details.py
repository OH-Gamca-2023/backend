# Generated by Django 4.2 on 2023-05-17 17:26

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('disciplines', '0018_remove_discipline_details_post_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='details',
            field=mdeditor.fields.MDTextField(blank=True, max_length=8000, null=True, verbose_name='Detaily'),
        ),
    ]