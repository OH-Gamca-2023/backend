from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Setting, AuthRestriction


@admin.register(Setting)
class SettingAdmin(ModelAdmin):
    list_display = ['key', 'value']
    list_editable = ['value']


@admin.register(AuthRestriction)
class AuthRestrictionAdmin(ModelAdmin):
    list_display = ['type', 'restricted', 'bypass_staff', 'bypass_admin', 'bypass_superuser', 'bypass_department']
    list_editable = ['restricted', 'bypass_staff', 'bypass_admin', 'bypass_superuser', 'bypass_department']

