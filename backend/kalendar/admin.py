from django.contrib import admin
from django_object_actions import DjangoObjectActions, action

from .generator import generate
from .models import Calendar, GenerationEvent, Event


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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('name', 'start_date', 'start_time', 'end_date', 'end_time', 'location')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name', 'location')
    ordering = ('start_date', 'start_time', 'end_date', 'end_time')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            generate(request, f'Event {obj.name} ({obj.id}) has been created')
        else:
            generate(request, f'Event {obj.name} ({obj.id}) has been modified [{", ".join(form.changed_data)}]')


@admin.register(GenerationEvent)
class GenerationEventAdmin(admin.ModelAdmin):
    list_display = ('cause', 'initiator', 'initiation_time', 'duration', 'was_successful', 'result', 'generated_id')
    list_filter = ('cause', 'initiator', 'was_successful')
    search_fields = ('cause', 'initiator', 'result', 'generated_id')
