# Generated by Django 4.2 on 2023-05-12 07:00

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_tag_alter_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.CharField(default=posts.models.gen_id, max_length=15, primary_key=True, serialize=False, unique=True),
        ),
    ]