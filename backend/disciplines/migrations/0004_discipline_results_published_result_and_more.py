# Generated by Django 4.1.7 on 2023-04-02 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_grade_permission_group_alter_user_is_admin'),
        ('disciplines', '0003_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='results_published',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discipline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='disciplines.discipline')),
                ('placements', models.ManyToManyField(through='disciplines.Placement', to='users.clazz')),
            ],
            options={
                'verbose_name': 'result',
                'verbose_name_plural': 'results',
            },
        ),
        migrations.AlterField(
            model_name='placement',
            name='results',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='disciplines.result'),
        ),
        migrations.DeleteModel(
            name='Results',
        ),
    ]