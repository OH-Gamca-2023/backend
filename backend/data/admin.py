from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Setting, AuthRestriction, Alert, ProfileEditPermissions, HueyTask


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
    list_display = ['user_type', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'discord_id', 'password']
    list_editable = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'discord_id', 'password']


@admin.register(HueyTask)
class HueyTaskAdmin(admin.ModelAdmin):
    actions_on_top = False
    list_display = ['id', 'uuid', 'name', 'signal', 'is_finished', 'retries_left', 'admin_timestamp']
    list_display_links = ['id']
    search_fields = ['uuid', 'name']

    @admin.display(description='Timestamp')
    def admin_timestamp(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # return False to permissions to disable add/changing/deleting in admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
