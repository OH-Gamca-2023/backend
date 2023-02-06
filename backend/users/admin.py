from django.db import models
from django.contrib import admin
from .models import Category, Clazz, User


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
