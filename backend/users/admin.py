from django.db import models
from django.contrib import admin
from .models import Category, Clazz, User
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

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'clazz', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'clazz')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2')}
         ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'clazz')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('last_login', 'date_joined')


admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ()


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_fake')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
    filter_horizontal = ()

    list_filter = ('category', 'is_fake')
