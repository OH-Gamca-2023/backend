from django.contrib import admin

from .models import Grade, Clazz, User, MicrosoftUser, UserToken
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'clazz')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_admin', 'is_superuser', 'clazz', 'date_joined')
    list_filter = ('is_staff', 'is_admin', 'is_superuser', 'is_active', 'groups', 'clazz')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'microsoft_user')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('type', 'is_active', 'is_staff', 'is_admin', 'is_superuser')}),
        ('Advanced permissions', {
            'classes': ('collapse',),
            'description': '<h3 style="color: red;"><b>Advanced permission settings. Only change these if you know '
                           'what you are doing ('
                           'preferably not at all).</b></h3>',
            'fields': ('groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'microsoft_user')}
         ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('last_login', 'date_joined', 'type')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                if obj.is_admin or obj.is_superuser:
                    if request.user.id != obj.id:
                        # user is not superuser and is editing an admin or superuser
                        # disable all fields
                        return self.readonly_fields + ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups',
                                                       'user_permissions', 'microsoft_user', 'username', 'email',
                                                       'password', 'first_name', 'last_name', 'clazz', 'groups',
                                                       'user_permissions', 'last_login', 'date_joined', 'type')
                    else:
                        # user is not superuser and is editing himself
                        # disable permission fields and microsoft user
                        return self.readonly_fields + ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups',
                                                       'user_permissions', 'microsoft_user')
                else:
                    # user is not superuser and is editing a normal user or organizer
                    # disable permission fields and microsoft user
                    return self.readonly_fields + (
                        'is_superuser', 'is_admin', 'groups', 'user_permissions', 'microsoft_user')

            # user is superuser and is editing himself
            if request.user.is_superuser and request.user.id == obj.id:
                return self.readonly_fields + ('is_active', 'is_staff', 'is_superuser')

        return self.readonly_fields


admin.site.register(User, UserAdmin)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'competing')
    search_fields = ('name', 'competing')
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