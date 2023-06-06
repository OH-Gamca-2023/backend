from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, path

from .models import *
from kalendar.generator import generate
# from .publishing import DetailsPublishView, ResultsPublishView


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
        ('Organising', {
            'fields': ('primary_organisers', 'teacher_supervisors'),
            'classes': ('collapse',),
            'description': '<b style="color: red;">Ak sa chcete prihlásiť na organizovanie disciplíny, použite '
                           'hlavnú stránku. V tomto rozhraní môžu organizátorov upratovať iba administrátori.</b>'
        }),
        ('Publishing', {
            'fields': ('date_published', 'details_published', 'results_published')
        }),
    )

    inlines = [
        ResultInline,
    ]

    add_fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'details')
        }),
        ('Categorisation', {
            'fields': ('category', 'target_grades')
        }),
        ('Date and time', {
            'fields': ('date', 'time', 'location', 'volatile_date')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets
        return self.add_fieldsets

    def get_inlines(self, request, obj):
        if obj:
            return self.inlines
        return []

    @admin.display(description='Result sets')
    def result_sets(self, obj):
        return Result.objects.filter(discipline=obj).count()

    @admin.display(description='Target grades')
    def target_grades_str(self, obj):
        return ", ".join([str(grade) for grade in obj.target_grades.all()])

    def save_model(self, request, obj, form, change):
        if change:
            # disable publishing multiple items at once
            items = ['date_published', 'details_published', 'results_published']
            modified = [item for item in form.changed_data if item in items]
            if len(modified) > 1:
                messages.warning(request, 'Only one item can be published at a time')
                for item in modified:
                    setattr(obj, item, False)
            else:
                modified = modified[0] if modified else None
                if modified:
                    messages.error(request, 'Publishing is temporarily disabled while a new system is being developed')
                    modified = None

                    if modified == 'date_published':
                        if not request.user.has_perm('disciplines.publish_details'):
                            messages.error(request, 'You do not have permission to publish details')
                            modified = None
                    elif modified == 'details_published':
                        if not request.user.has_perm('disciplines.publish_details'):
                            messages.error(request, 'You do not have permission to publish details')
                            modified = None
                    elif modified == 'results_published':
                        if not request.user.has_perm('disciplines.publish_results'):
                            messages.error(request, 'You do not have permission to publish results')
                            modified = None

                request.POST._mutable = True
                request.POST['_published'] = modified

        super().save_model(request, obj, form, change)
        if not change:
            generate(request, f'Discipline {obj.name} ({obj.id}) has been created')
        else:
            generate(request, f'Discipline {obj.name} ({obj.id}) has been modified [{", ".join(form.changed_data)}]')

    def response_change(self, request, obj):
        super_response = super().response_change(request, obj)

        if request.POST['_published']:
            if request.POST['_published'] == 'details_published':
                # redirect user to post creation page
                messages.info(request, 'Detaily budú zverejnené. Tu môžete urobiť posledné úpravy príspevku.')
                return HttpResponseRedirect(reverse('admin:disciplines_publish_details', args=[obj.id]))
            elif request.POST['_published'] == 'results_published':
                messages.info(request, 'Výsledky budú zverejnené. Tu môžete urobiť posledné úpravy príspevku.')
                return HttpResponseRedirect(reverse('admin:disciplines_publish_results', args=[obj.id]))

        return super_response

    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj:
            if obj.date_published:
                readonly.append('date_published')
            if obj.details_published:
                readonly.append('details_published')
            if obj.results_published:
                readonly.append('results_published')

        if not request.user.has_perm('disciplines.modify_people'):
            readonly += ['primary_organisers', 'teacher_oversight']

        return readonly

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('<str:discipline_id>/publish/details/', admin.site.admin_view(DetailsPublishView.as_view()), name='disciplines_publish_details'),
    #         path('<str:discipline_id>/publish/results/', admin.site.admin_view(ResultsPublishView.as_view()), name='disciplines_publish_results'),
    #     ]
    #     return custom_urls + urls


class PlacementInline(TabularInline):
    model = Placement
    extra = 0
    fields = ('clazz', 'place')

    # limit choices to classes in the grade of the results or fake classes
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'clazz':
            if request.resolver_match.kwargs.get('object_id'):
                results = Result.objects.get(id=request.resolver_match.kwargs.get('object_id'))
                kwargs["queryset"] = Clazz.objects.filter(Q(grade__in=results.grades.all()) | Q(is_fake=True))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'discipline')
    search_fields = ('discipline__name',)

    @admin.display(description='Placements')
    def placements(self, obj):
        return obj.placement_set.count()

    def get_inlines(self, request, obj):
        if obj:
            return [PlacementInline]
        messages.warning(request, 'Pred pridaním umiestnení je potrebné vytvoriť výsledkovku')
        return []

    def response_add(self, request, obj, post_url_continue=None):
        for grade in obj.grades.all():
            for clazz in grade.classes.all():
                Placement.objects.get_or_create(result=obj, clazz=clazz)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        all_classes = Clazz.objects.filter(grade__in=obj.grades.all())
        for clazz in all_classes:
            Placement.objects.get_or_create(result=obj, clazz=clazz)
        for placement in obj.placements.all():
            if placement.clazz not in all_classes and not placement.clazz.is_fake:
                placement.delete()
        return super().response_change(request, obj)


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'clazz', 'place', 'participated')
    list_filter = ('result__discipline', 'clazz')
