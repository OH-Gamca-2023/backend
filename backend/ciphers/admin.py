from django.contrib import admin

from .models import *


@admin.register(Cipher)
class CipherAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'started', 'hint_visible', 'has_ended')
    list_filter = ('start', 'end')
    search_fields = ('name',)
    ordering = ('start', 'end')

    fieldsets = (
        ('General', {
            'fields': ('name', 'task_file', 'start', 'end', 'correct_answer')
        }),
        ('Hint', {
            'fields': ('hint_text', 'hint_publish_time')
        }),
        ('Advanced', {
            'fields': ('ignore_case', 'ignore_intermediate_whitespace', 'ignore_trailing_leading_whitespace',
                       'ignore_accents', 'submission_delay', 'max_submissions_per_day')
            'classes': ('collapse',),
            'description': '<b><h3 style="color: red;">Advanced settings</h3><br>Only editable with special '
                           'permissions. You most  likely don\'t want to change these.</b>'
        })
    )

    @admin.display(description='Started', boolean=True)
    def started(self, obj):
        return obj.started

    @admin.display(description='Hint visible', boolean=True)
    def hint_visible(self, obj):
        return obj.hint_visible

    @admin.display(description='Ended', boolean=True)
    def has_ended(self, obj):
        return obj.has_ended

    def get_readonly_fields(self, request, obj=None):
        base = super().get_readonly_fields(request, obj)

        if not request.user.has_perm("ciphers.change_cipher_advanced"):
            base += ('ignore_case', 'ignore_intermediate_whitespace', 'ignore_trailing_leading_whitespace',
                     'ignore_accents', 'submission_delay')

        return base


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'cipher', 'clazz', 'competing', 'answer', 'time', 'after_hint', 'correct')
    list_filter = ('cipher', 'clazz', 'after_hint', 'correct')
    search_fields = ('answer',)
    ordering = ('time',)
    autocomplete_fields = ('cipher', 'clazz', 'submitted_by')

    list_display_links = ('pk', '__str__')

    @admin.display(description='Súťažné', boolean=True)
    def competing(self, obj):
        return obj.clazz.grade.cipher_competing
