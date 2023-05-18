from django.contrib import admin

from .models import *


@admin.register(Cipher)
class CipherAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'started', 'hint_visible', 'has_ended')
    list_filter = ('start', 'end')
    search_fields = ('name',)
    ordering = ('start', 'end')

    @admin.display(description='Started', boolean=True)
    def started(self, obj):
        return obj.started

    @admin.display(description='Hint visible', boolean=True)
    def hint_visible(self, obj):
        return obj.hint_visible

    @admin.display(description='Ended', boolean=True)
    def has_ended(self, obj):
        return obj.has_ended


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'cipher', 'clazz', 'answer', 'time', 'after_hint', 'correct')
    list_filter = ('cipher', 'clazz', 'after_hint', 'correct')
    search_fields = ('answer',)
    ordering = ('time',)

    list_display_links = ('pk', '__str__')
