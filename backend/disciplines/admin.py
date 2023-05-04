from django.contrib import admin

from .models import *
from kalendar.generator import generate


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'disciplines')
    list_display_links = ('id', 'name')
    search_fields = ('name',)

    @admin.display(description='Disciplines')
    def disciplines(self, obj):
        return obj.discipline_set.count()


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0
    show_change_link = True


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'target_grades_str', 'date', 'time', 'date_published', 'details_published',
                    'results_published', 'result_sets')
    list_filter = ('date_published', 'details_published', 'category', 'target_grades')
    search_fields = ('name', 'description')
    date_hierarchy = 'date'

    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'details')
        }),
        ('Categorisation', {
            'fields': ('category', 'target_grades')
        }),
        ('Date and time', {
            'fields': ('date', 'time', 'location', 'volatile_date')
        }),
        ('Publishing', {
            'fields': ('date_published', 'details_published')
        }),
        ('Results', {
            'fields': ('results_published',)
        }),
    )

    inlines = [
        ResultInline,
    ]

    add_fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'description')
        }),
        ('Categorisation', {
            'fields': ('category', 'tags', 'target_grades')
        }),
        ('Date and time', {
            'fields': ('date', 'time', 'location', 'volatile_date')
        })
    )

    @admin.display(description='Result sets')
    def result_sets(self, obj):
        return Result.objects.filter(discipline=obj).count()

    @admin.display(description='Target grades')
    def target_grades_str(self, obj):
        return ", ".join([str(grade) for grade in obj.target_grades.all()])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            generate(request, f'Discipline {obj.name} ({obj.id}) has been created')
        else:
            # check if anything date-related has changed
            listening = ['date', 'time', 'volatile_date', 'date_published', 'name', 'short_name']
            modified = list(filter(lambda x: x in form.changed_data, listening))
            if len(modified) > 0:
                # if so, generate the calendar
                generate(request, f'Discipline {obj.name} ({obj.id}) has been modified [{", ".join(modified)}]')


class PlacementInline(admin.TabularInline):
    model = Placement
    extra = 1


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('name', 'discipline')
    search_fields = ('discipline__name',)

    inlines = [
        PlacementInline,
    ]

    @admin.display(description='Placements')
    def placements(self, obj):
        return obj.placement_set.count()
