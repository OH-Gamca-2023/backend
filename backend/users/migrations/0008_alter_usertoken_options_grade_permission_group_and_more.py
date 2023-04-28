# Generated by Django 4.1.7 on 2023-03-19 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0007_alter_grade_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usertoken',
            options={'verbose_name': 'user token', 'verbose_name_plural': 'user tokens'},
        ),
        migrations.AddField(
            model_name='grade',
            name='permission_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.group'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='name',
            field=models.CharField(choices=[('2. Stupeň', '2. Stupeň'), ('3. Stupeň', '3. Stupeň'), ('Organizátori', 'Organizátori'), ('Učitelia', 'Učitelia'), ('Alumni', 'Alumni')], max_length=100, unique=True),
        ),
    ]