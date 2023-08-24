from django.contrib import admin
from django_object_actions import action, DjangoObjectActions

from .models import Grade, Clazz, User, MicrosoftUser
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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm

    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'clazz', 'date_joined')
    list_display_links = ('id', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'clazz')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'microsoft_user')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz', 'phone_number', 'discord_id')}),
        ('Permissions', {'fields': ('type', 'is_active', 'is_staff', 'is_superuser', 'individual_cipher_solving',
                                    'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'microsoft_user')}
         ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz', 'phone_number', 'discord_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('last_login', 'date_joined', 'type')


@admin.register(Grade)
class GradeAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('id', 'name', 'competing', 'cipher_competing', 'is_organiser', 'is_teacher')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('competing', 'cipher_competing')
    ordering = ('id',)

    @action(description='Create grades', permissions=['add'])
    def create_grades(self, request, queryset):
        for name in Grade.grade_options:
            Grade.objects.get_or_create(name=name[0], competing=name[0] in ['2. Stupeň', '3. Stupeň'],
                                        cipher_competing=name[0] in ['2. Stupeň', 'Organizátori'],
                                        is_organiser=name[0] in ['Organizátori'],
                                        is_teacher=name[0] in ['Učitelia'])

    changelist_actions = ('create_grades',)


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade', 'is_fake')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'grade__name')
    ordering = ('name',)

    list_filter = ('grade', 'is_fake')


@admin.register(MicrosoftUser)
class MicrosoftUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mail', 'display_name', 'job_title', 'department')
    list_display_links = ('id',)

    search_fields = ('user__email', 'microsoft_id', 'mail', 'display_name')
    ordering = ('department', 'display_name')
    filter_horizontal = ()

    list_filter = ('department', 'job_title')

