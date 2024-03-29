# Generated by Django 4.2.1 on 2023-06-16 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_remove_post_disable_comments_delete_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'permissions': [('change_others_post', 'Can change posts of other users'), ('delete_others_post', 'Can delete posts of other users')], 'verbose_name': 'príspevok', 'verbose_name_plural': 'príspevky'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'permissions': [('add_special_tag', 'Can add special tag'), ('change_special_tag', 'Can change special tag'), ('delete_special_tag', 'Can delete special tag')], 'verbose_name': 'tag', 'verbose_name_plural': 'tagy'},
        ),
    ]
