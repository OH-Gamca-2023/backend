from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class Grade(models.Model):
    grade_options = (
        ('2. Stupeň', '2. Stupeň'),
        ('3. Stupeň', '3. Stupeň'),
        ('Organizátori', 'Organizátori'),
        ('Učitelia', 'Učitelia'),
        ('Alumni', 'Alumni')
    )
    name = models.CharField("Názov", max_length=100, choices=grade_options, unique=True)
    competing = models.BooleanField("Súťažná?", default=True)
    cipher_competing = models.BooleanField("Súťaží v online šifrovačke?", default=False)

    is_organiser = models.BooleanField("Je organizátorská?", default=False)
    is_teacher = models.BooleanField("Je učiteľská?", default=False)

    permission_group = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'stupne'
        verbose_name = 'stupeň'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        raise Exception('Grade objects cannot be deleted.')


class Clazz(models.Model):
    name = models.CharField("Názov", max_length=100)
    grade = models.ForeignKey('users.Grade', on_delete=models.CASCADE, verbose_name="Stupeň", related_name="classes")
    is_fake = models.BooleanField("Je nesúťažná", default=False)
    microsoft_department = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'triedy'
        verbose_name = 'trieda'

    def __str__(self):
        return self.name


class MicrosoftUser(models.Model):
    id = models.CharField("Microsoft ID", max_length=150, primary_key=True)
    mail = models.CharField(max_length=150)

    display_name = models.CharField(max_length=150)
    given_name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)

    job_title = models.CharField(max_length=150)
    office_location = models.CharField(max_length=150)
    department = models.CharField(max_length=150)

    def get_clazz(self):
        return Clazz.objects.filter(microsoft_department=self.department).first()

    def __str__(self):
        return self.display_name + ' (' + self.id + ')'

    class Meta:
        verbose_name_plural = 'Microsoft používatelia'
        verbose_name = 'Microsoft používateľ'


class CustomUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related('clazz__grade')


class User(AbstractUser):
    objects = CustomUserManager()

    clazz = models.ForeignKey('users.Clazz', on_delete=models.CASCADE, null=True, blank=True)

    username = models.CharField(
        "Používateľské meno",
        max_length=150,
        unique=True,
        help_text="Vyžadované. Max. 150 znakov.",
        error_messages={
            "unique": "Používateľ s týmto používateľským menom už existuje."
        },
    )
    email = models.EmailField(_("email address"), blank=True, unique=True)

    phone_number = PhoneNumberField("Telefónne číslo", null=True, blank=True)

    microsoft_user = models.OneToOneField(MicrosoftUser, on_delete=models.CASCADE, null=True, blank=True,
                                          verbose_name="Microsoft používateľ")

    individual_cipher_solving = models.BooleanField("Môže riešiť šifrovačku individuálne", default=False, help_text=
                                                    "Používateľ môže riešiť šifrovačku individuálne, bez priradenia do " 
                                                    "triedy. Ak trieda používateľa súťaží v online šifrovačke, táto "
                                                    "možnosť nemá žiadny efekt.")

    def type(self):
        if self.is_superuser:
            return 'admin'
        if self.clazz is not None:
            if self.clazz.grade.is_organiser:
                return 'organiser'
            if self.clazz.grade.is_teacher:
                return 'teacher'
            if self.clazz.grade.name == 'Alumni':
                return 'alumni'
            return 'student'
        return 'unknown'

    def has_password(self):
        return self.password != ''

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id:
            old = User.objects.get(id=self.id)
            if old.clazz != self.clazz:
                if old.clazz and old.clazz.grade.permission_group:
                    self.groups.remove(old.clazz.grade.permission_group)
                if self.clazz and self.clazz.grade.permission_group:
                    self.groups.add(self.clazz.grade.permission_group)
            super().save(force_insert, force_update, using, update_fields)
        else:
            super().save(force_insert, force_update, using, update_fields)
            if self.clazz and self.clazz.grade.permission_group:
                self.groups.add(self.clazz.grade.permission_group)
            super().save()