
from django.contrib import admin

from .models import Calendar, GenerationEvent, GenerationRequest


@admin.register(GenerationRequest)
class GenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('cause', 'initiator', 'time')
    list_filter = ('initiator', )


admin.site.register(Calendar)
admin.site.register(GenerationEvent)
