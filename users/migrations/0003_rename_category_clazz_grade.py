# Generated by Django 4.1.7 on 2023-03-15 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_microsoftuser_rename_category_grade_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clazz',
            old_name='category',
            new_name='grade',
        ),
    ]
