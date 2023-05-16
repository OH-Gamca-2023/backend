from django.contrib import admin
from django_object_actions import DjangoObjectActions, action

from .generator import generate
from .models import Calendar, GenerationEvent


@admin.register(Calendar)
class CalendarAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('key', 'content_type', 'is_current', 'id')
    list_filter = ('content_type', 'is_current')
    search_fields = ('key', 'is_current', 'id')

    @action(description='Vygeneruje kalendár disciplín. Ak už existuje, prepíše ho.', permissions=['generate'],
            label='Vygenerovať')
    def generate(self, request, obj):
        generate(request, 'Manual request from admin panel')

    changelist_actions = ('generate',)


@admin.register(GenerationEvent)
class GenerationEventAdmin(admin.ModelAdmin):
    list_display = ('cause', 'initiator', 'initiation_time', 'duration', 'was_successful', 'result', 'generated_id')
    list_filter = ('cause', 'initiator', 'was_successful')
    search_fields = ('cause', 'initiator', 'result', 'generated_id')
