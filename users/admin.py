import datetime
import re

from django.db import models
from django.contrib import admin
from django.utils import timezone

from .models import Grade, Clazz, User, MicrosoftUser, UserToken
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'clazz')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'clazz', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'clazz')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'microsoft_user')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'microsoft_user')}
         ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('last_login', 'date_joined')


admin.site.register(User, UserAdmin)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ()


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'is_fake')
    search_fields = ('name', 'grade__name')
    ordering = ('name',)
    filter_horizontal = ()

    list_filter = ('grade', 'is_fake')


@admin.register(MicrosoftUser)
class MicrosoftUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'mail', 'display_name', 'job_title', 'department', 'id')
    search_fields = ('user__email', 'microsoft_id', 'mail', 'display_name')
    ordering = ('department', 'display_name')
    filter_horizontal = ()

    list_filter = ('department', 'job_title')

    readonly_fields = (
        'id', 'mail', 'display_name', 'given_name', 'surname', 'job_title', 'office_location', 'department')


class UserTokenChangeForm(forms.ModelForm):
    class Meta:
        model = UserToken
        fields = ('invalid',)

    def clean_token(self):
        return self.initial["token"]


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    form = UserTokenChangeForm
    list_display = ('user', 'created', 'expires', 'token_censored', 'is_expired', 'invalid')
    search_fields = ('user__email', 'user__name')
    ordering = ('-created',)
    filter_horizontal = ()
    exclude = ('token',)

    readonly_fields = ('user', 'created', 'expires', 'token')

    list_filter = ('invalid',)

    def is_expired(self, obj):
        return timezone.now() > obj.expires

    def token_censored(self, obj):
        return re.sub(r'(?<=.{7}).(?=.{7})', '*', obj.token)
