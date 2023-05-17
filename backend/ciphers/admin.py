from django.contrib import admin
from .models import *


@admin.register(Cipher)
class CipherAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'visible', 'hint_visible', 'has_ended')
    list_filter = ('start', 'end', 'visible', 'hint_visible', 'has_ended')
    search_fields = ('name',)
    ordering = ('start', 'end')

    readonly_fields = ('visible', 'hint_visible', 'has_ended')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'cipher', 'clazz', 'answer', 'time', 'after_hint', 'correct')
    list_filter = ('cipher', 'clazz', 'after_hint', 'correct')
    search_fields = ('answer',)
    ordering = ('time',)

    list_display_links = ('pk', '__str__')
