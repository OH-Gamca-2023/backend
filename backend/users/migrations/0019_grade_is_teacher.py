# Generated by Django 4.2.1 on 2023-06-04 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='is_teacher',
            field=models.BooleanField(default=False, verbose_name='Je učiteľská?'),
        ),
    ]