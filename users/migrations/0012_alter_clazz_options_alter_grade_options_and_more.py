# Generated by Django 4.2 on 2023-04-04 15:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_grade_permission_group_alter_user_is_admin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clazz',
            options={'verbose_name': 'trieda', 'verbose_name_plural': 'triedy'},
        ),
        migrations.AlterModelOptions(
            name='grade',
            options={'verbose_name': 'stupeň', 'verbose_name_plural': 'stupne'},
        ),
        migrations.AlterModelOptions(
            name='microsoftuser',
            options={'verbose_name': 'Microsoft používateľ', 'verbose_name_plural': 'Microsoft používatelia'},
        ),
        migrations.AlterModelOptions(
            name='usertoken',
            options={'verbose_name': 'prístupový kód', 'verbose_name_plural': 'prístupové kódy'},
        ),
        migrations.AlterField(
            model_name='clazz',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.grade', verbose_name='Stupeň'),
        ),
        migrations.AlterField(
            model_name='clazz',
            name='is_fake',
            field=models.BooleanField(default=False, verbose_name='Je nesúťažná'),
        ),
        migrations.AlterField(
            model_name='clazz',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Názov'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='name',
            field=models.CharField(choices=[('2. Stupeň', '2. Stupeň'), ('3. Stupeň', '3. Stupeň'), ('Organizátori', 'Organizátori'), ('Učitelia', 'Učitelia'), ('Alumni', 'Alumni')], max_length=100, unique=True, verbose_name='Názov'),
        ),
        migrations.AlterField(
            model_name='microsoftuser',
            name='id',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, verbose_name='Microsoft ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, help_text='Používateľ je administrátorom. Administrátori majú viac práv ako štandardní organizátori.', verbose_name='Administátor'),
        ),
        migrations.AlterField(
            model_name='user',
            name='microsoft_user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.microsoftuser', verbose_name='Microsoft používateľ'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Používateľ s týmto používateľským menom už existuje.'}, help_text='Vyžadované. Max. 150 znakov.', max_length=150, unique=True, verbose_name='Používateľské meno'),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Vytvorený'),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='expires',
            field=models.DateTimeField(verbose_name='Platný do'),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='invalid',
            field=models.BooleanField(default=False, verbose_name='Neplatný'),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='token',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, verbose_name='Kód'),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Používateľ'),
        ),
    ]
