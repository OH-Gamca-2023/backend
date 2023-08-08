from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Setting, AuthRestriction, Alert, ProfileEditPermissions


@admin.register(Setting)
class SettingAdmin(ModelAdmin):
    list_display = ['key', 'value', 'exposed']
    list_editable = ['value', 'exposed']


@admin.register(AuthRestriction)
class AuthRestrictionAdmin(ModelAdmin):
    list_display = ['type', 'restricted', 'full', 'bypass_staff', 'bypass_superuser', 'bypass_department']
    list_editable = ['restricted', 'full', 'bypass_staff', 'bypass_superuser', 'bypass_department']

    def changelist_view(self, request, extra_context=None):
        self.message_user(request, 'Akákoľvek zmena týchto nastavení odhlási všetkých používateľov a zruší platnosť '
                                   'všetkých prístupových kódov.', level='warning')

        return super().changelist_view(request, extra_context)


@admin.register(Alert)
class AlertAdmin(ModelAdmin):
    list_display = ['id', 'message', 'type', 'show_on_site', 'show_in_admin', 'created_at', 'lasts_until', 'active']
    list_editable = ['show_on_site', 'show_in_admin', 'lasts_until', 'active']
    list_filter = ['type', 'show_on_site', 'show_in_admin', 'active']
    search_fields = ['message']

    readonly_fields = ['id', 'created_at']
    fieldsets = [
        (None, {
            'fields': ['id', 'message', 'type', ('show_on_site', 'show_in_admin'), ('created_at', 'lasts_until'), 'active']
        }),
    ]


@admin.register(ProfileEditPermissions)
class ProfileEditPermissionsAdmin(ModelAdmin):
    list_display = ['user_type', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'password']
    list_editable = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password']
