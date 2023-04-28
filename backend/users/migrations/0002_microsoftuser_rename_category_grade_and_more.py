# Generated by Django 4.1.7 on 2023-03-15 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_rename_affected_categories_post_affected_grades'),
        ('disciplines', '0003_category_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicrosoftUser',
            fields=[
                ('id', models.CharField(max_length=150, primary_key=True, serialize=False)),
                ('mail', models.CharField(max_length=150)),
                ('display_name', models.CharField(max_length=150)),
                ('given_name', models.CharField(max_length=150)),
                ('surname', models.CharField(max_length=150)),
                ('job_title', models.CharField(max_length=150)),
                ('office_location', models.CharField(max_length=150)),
                ('department', models.CharField(max_length=150)),
            ],
        ),
        migrations.RenameModel(
            old_name='Category',
            new_name='Grade',
        ),
        migrations.AlterModelOptions(
            name='clazz',
            options={'verbose_name': 'class', 'verbose_name_plural': 'classes'},
        ),
        migrations.AlterModelOptions(
            name='grade',
            options={'verbose_name': 'grade', 'verbose_name_plural': 'grades'},
        ),
        migrations.RemoveField(
            model_name='user',
            name='oauth_refresh_token',
        ),
        migrations.RemoveField(
            model_name='user',
            name='oauth_token',
        ),
        migrations.AddField(
            model_name='clazz',
            name='microsoft_department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='microsoft_user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.microsoftuser'),
        ),
    ]