# Generated by Django 4.2 on 2023-05-17 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_alter_post_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='special',
            field=models.CharField(blank=True, help_text='Používané interne. NEUPRAVUJTE ak neviete čo robíte.', max_length=10, null=True, verbose_name='Špeciálna funkcia'),
        ),
    ]