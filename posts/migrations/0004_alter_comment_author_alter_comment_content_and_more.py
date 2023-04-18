# Generated by Django 4.2 on 2023-04-04 15:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0012_alter_clazz_options_alter_grade_options_and_more'),
        ('disciplines', '0008_alter_category_options_alter_placement_options_and_more'),
        ('posts', '0003_rename_affected_categories_post_affected_grades'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.CharField(help_text='Ak je autor príspevku organizátor, obsah bude prehnaný cez Markdown.', max_length=10000, verbose_name='Obsah'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Dátum'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='posts.comment', verbose_name='Rodičovský komentár'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post', verbose_name='Príspevok'),
        ),
        migrations.AlterField(
            model_name='post',
            name='affected_grades',
            field=models.ManyToManyField(blank=True, related_name='posts_for_category', to='users.grade', verbose_name='Ovplyvnené stupne'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.CharField(help_text='Obsah príspevku bude prehnaný cez Markdown.', max_length=10000, verbose_name='Obsah'),
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Dátum'),
        ),
        migrations.AlterField(
            model_name='post',
            name='disable_comments',
            field=models.BooleanField(default=False, verbose_name='Vypnuté komentáre'),
        ),
        migrations.AlterField(
            model_name='post',
            name='related_disciplines',
            field=models.ManyToManyField(blank=True, related_name='posts_for_discipline', to='disciplines.discipline', verbose_name='Súvisiace disciplíny'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts_for_tag', to='disciplines.tag', verbose_name='Tagy'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Nadpis'),
        ),
    ]
