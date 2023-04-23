from django.contrib import admin

from .models import Calendar, GenerationEvent


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('key', 'content_type', 'is_current', 'id')
    list_filter = ('content_type', 'is_current')
    search_fields = ('key', 'is_current', 'id')


@admin.register(GenerationEvent)
class GenerationEventAdmin(admin.ModelAdmin):
    list_display = ('cause', 'initiator', 'initiation_time', 'duration', 'was_successful', 'result', 'generated_id')
    list_filter = ('cause', 'initiator', 'was_successful')
    search_fields = ('cause', 'initiator', 'result', 'generated_id')
