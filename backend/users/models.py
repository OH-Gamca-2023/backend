from django.contrib.auth.models import AbstractUser, Permission
from django.db import models

from data.permissions import admin_module_permissions, organizer_module_permissions, default_module_permissions, matches, \
    blacklist, organizer, admin, default, force_blacklist


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

    class Meta:
        verbose_name_plural = 'stupne'
        verbose_name = 'stupeň'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        raise Exception('Grade objects cannot be deleted.')


class Clazz(models.Model):
    name = models.CharField("Názov", max_length=100)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Stupeň", related_name="classes")
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


class User(AbstractUser):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)

    username = models.CharField(
        "Používateľské meno",
        max_length=150,
        unique=True,
        help_text="Vyžadované. Max. 150 znakov.",
        error_messages={
            "unique": "Používateľ s týmto používateľským menom už existuje."
        },
    )

    is_admin = models.BooleanField("Administátor", default=False,
                                      help_text="Používateľ je administrátorom. Administrátori majú viac práv ako "
                                                "štandardní organizátori.")

    microsoft_user = models.OneToOneField(MicrosoftUser, on_delete=models.CASCADE, null=True, blank=True,
                                          verbose_name="Microsoft používateľ")

    def type(self):
        if self.is_superuser or self.is_admin:
            return 'admin'
        elif self.clazz.grade.name == 'Organizátori':
            return 'organizer'
        elif self.clazz.grade.name == 'Učitelia':
            return 'teacher'
        elif self.clazz.grade.name == 'Alumni':
            return 'alumni'
        else:
            return 'student'

    def has_password(self):
        return self.password != ''

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        if isinstance(perm, Permission):
            perm = perm.content_type.app_label + '.' + perm.codename

        if matches(force_blacklist, perm):
            return False

        if self.is_superuser:
            return True
        elif super().has_perm(perm, obj):
            return True

        if matches(blacklist, perm):
            return False

        if self.is_admin:
            if matches(admin, perm):
                return True

        if self.is_staff:
            if matches(organizer, perm):
                return True

        return matches(default, perm)

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        elif not self.is_active:
            return False

        if self.is_admin:
            return app_label in admin_module_permissions
        elif self.is_staff:
            return app_label in organizer_module_permissions
        else:
            return app_label in default_module_permissions or super().has_module_perms(app_label)

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def get_user_permissions(self, obj=None):
        return set(filter(self.has_perm, Permission.objects.all()))

    def get_all_permissions(self, obj=None):
        return self.get_user_permissions(obj).union(self.get_user_permissions(obj))
