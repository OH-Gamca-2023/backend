# Generated by Django 4.2 on 2023-05-12 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_tag_alter_post_tags'),
        ('disciplines', '0016_alter_discipline_short_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
