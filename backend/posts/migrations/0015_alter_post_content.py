# Generated by Django 4.2.4 on 2023-09-16 12:30

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_alter_post_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=mdeditor.fields.MDTextField(blank=True, max_length=20000, null=True, verbose_name='Obsah'),
        ),
    ]
