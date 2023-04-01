import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Grade(models.Model):
    grade_options = (
        ('2. Stupeň', '2. Stupeň'),
        ('3. Stupeň', '3. Stupeň'),
        ('Organizátori', 'Organizátori'),
        ('Učitelia', 'Učitelia'),
        ('Alumni', 'Alumni')
    )
    name = models.CharField(max_length=100, choices=grade_options, unique=True)

    class Meta:
        verbose_name_plural = 'grades'
        verbose_name = 'grade'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        raise Exception('Grade objects cannot be deleted.')


@receiver(post_save, sender=Grade)
def create_grades(sender, instance, created, **kwargs):
    if not created:
        return
    for name in Grade.grade_options:
        Grade.objects.get_or_create(name=name[0])


class Clazz(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    is_fake = models.BooleanField(default=False)
    microsoft_department = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'classes'
        verbose_name = 'class'

    def __str__(self):
        return self.name


class MicrosoftUser(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
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


class User(AbstractUser):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    is_admin = models.BooleanField(_("admin"), default=False,
                                   help_text=_('Specifies whether the user has admin privileges. '
                                               'Has more privileges than regular staff but not as much as superuser.'))

    microsoft_user = models.OneToOneField(MicrosoftUser, on_delete=models.CASCADE, null=True, blank=True)

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
        if self.is_superuser:
            return True

        group, action = perm.split('.') if '.' in perm else (perm, '')
        if self.is_admin:
            if group == 'users':
                if action.startswith('view'):
                    return not action.endswith('usertoken')
                else:
                    if perm == 'users.change_user':
                        return True

        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True

        if self.is_admin:
            if app_label == 'users':
                return True

        return super().has_module_perms(app_label)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True


profile_edit_permission = {
    'student': [],
    'alumni': ['email'],
    'teacher': ['email'],
    'organizer': ['email', 'username', 'password'],
    'admin': ['first_name', 'last_name', 'email', 'username', 'password'],
}


class UserToken(models.Model):
    token = models.CharField(max_length=150, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    invalid = models.BooleanField(default=False)

    def token_censored(self):
        return re.sub(r'(?<=.{7}).(?=.{7})', '*', self.token)

    def is_expired(self):
        return timezone.now() > self.expires

    def __str__(self):
        return self.user.username + ' - ' + self.token_censored() + (
            '(invalid)' if self.invalid else ('(expired)' if self.is_expired() else ''))

    class Meta:
        verbose_name_plural = 'user tokens'
        verbose_name = 'user token'
