from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django_object_actions import DjangoObjectActions, action

from .models import *
from backend.kalendar.generator import generate
from .tasks import send_7day_notification, send_3day_notification, send_1day_notification
from .views.publishing import DetailsPublishView, ResultsPublishView
from backend.posts.models import Post, Tag
from ..users.models import Clazz


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
    autocomplete_fields = ('categories', 'grades')


@admin.register(Discipline)
class DisciplineAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'category', 'target_grades_str', 'date', 'start_time', 'end_time', 'date_published', 'details_published',
                    'results_published', 'result_sets')
    list_filter = ('date_published', 'details_published', 'category', 'target_grades')
    search_fields = ('name', 'details')
    date_hierarchy = 'date'
    ordering = ('date', 'start_time')

    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'details', 'teacher_supervisors_enabled')
        }),
        ('Kategorizácia', {
            'fields': ('category', 'target_grades')
        }),
        ('Dátum, čas a miesto', {
            'fields': ('date', 'start_time', 'end_time', 'location')
        }),
        ('Organizátori', {
            'fields': ('primary_organisers', 'teacher_supervisors'),
            'classes': ('collapse',),
            'description': '<b style="color: red;">Ak sa chcete prihlásiť na organizovanie disciplíny, použite '
                           'hlavnú stránku. V tomto rozhraní môžu organizátorov upratovať iba administrátori.</b>'
        }),
        ('Zverejňovanie', {
            'fields': ('date_published', 'details_published', 'results_published')
        }),
        ('Detaily výsledkov', {
            'fields': ('result_details',),
            'classes': ('collapse',)
        }),
    )

    inlines = [
        ResultInline,
    ]

    add_fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'details', 'teacher_supervisors_enabled')
        }),
        ('Kategorizácia', {
            'fields': ('category', 'target_grades')
        }),
        ('Dátum, čas a miesto', {
            'fields': ('date', 'start_time', 'end_time', 'location')
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
            items = ['details_published', 'results_published']
            modified = [item for item in form.changed_data if item in items]
            if len(modified) > 1:
                messages.warning(request, 'Only one of properties "details published" and "results published" can be '
                                          'changed at once')
                for item in modified:
                    setattr(obj, item, not getattr(obj, item))
            elif len(modified) == 1:
                if getattr(obj, modified[0]):
                    request.POST._mutable = True
                    request.POST['_published'] = modified[0]
                    request.POST._mutable = False
                else:
                    details_post = Post.objects.filter(related_disciplines=obj, tags=Tag.objects.get(special='info' if
                                                       modified[0] == 'details_published' else 'results'))
                    if details_post.exists():
                        details_post = details_post.first()
                        details_post.delete()
                    messages.info(request, 'Príspevok zverejňujúci detaily/výsledky bol odstránený.')

        super().save_model(request, obj, form, change)
        if not change:
            generate(request, f'Discipline {obj.name} ({obj.id}) has been created')
        else:
            generate(request, f'Discipline {obj.name} ({obj.id}) has been modified [{", ".join(form.changed_data)}]')

    def response_change(self, request, obj):
        super_response = super().response_change(request, obj)

        if '_published' in request.POST:
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
            fields = ['date_published', 'details_published', 'results_published']
            for field in fields:
                if getattr(obj, field) and not request.user.has_perm('disciplines.hide_published'):
                    readonly.append(field)
                elif not request.user.has_perm(f'disciplines.publish_{field.split("_")[0]}'):
                    readonly.append(field)

        if not request.user.has_perm('disciplines.modify_people'):
            readonly += ['primary_organisers', 'teacher_oversight']

        return readonly

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:discipline_id>/publish/details/', admin.site.admin_view(DetailsPublishView.as_view()),
                 name='disciplines_publish_details'),
            path('<str:discipline_id>/publish/results/', admin.site.admin_view(ResultsPublishView.as_view()),
                 name='disciplines_publish_results'),
        ]
        return custom_urls + urls

    @action(description='Pošle upozornenie zodpovedným organizátorom', permissions=['disciplines.send_notification'],
            label='Pošli upozornenie')
    def send_notification(self, request, queryset):
        send_7day_notification()()
        send_3day_notification()()
        send_1day_notification()()
        messages.success(request, 'Požiadavka na poslanie upozornení bola zaznamenaná.')

    changelist_actions = ['send_notification']


class PlacementInline(TabularInline):
    model = Placement
    extra = 0
    fields = ('clazz', 'place', 'detail')

    # limit choices to classes in the grade of the results or fake classes
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'clazz':
            if request.resolver_match.kwargs.get('object_id'):
                results = Result.objects.get(id=request.resolver_match.kwargs.get('object_id'))
                kwargs["queryset"] = Clazz.objects.filter(Q(grade__in=results.grades.all()) | Q(is_fake=True))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'discipline', 'get_grades', 'autofill', 'get_placements')
    list_filter = ('discipline', 'grades')
    search_fields = ('discipline__name',)
    autocomplete_fields = ('discipline', 'categories', 'grades')

    @admin.display(description='Grades')
    def get_grades(self, obj):
        return ", ".join([str(grade) for grade in obj.grades.all()])

    @admin.display(description='Placements')
    def get_placements(self, obj):
        return obj.placements.count()

    def get_inlines(self, request, obj):
        if obj:
            return [PlacementInline]
        messages.warning(request, 'Pred pridaním umiestnení je potrebné vytvoriť výsledkovku')
        return []

    def response_add(self, request, obj, post_url_continue=None):
        if obj.autofill:
            for grade in obj.grades.all():
                for clazz in grade.classes.all():
                    Placement.objects.get_or_create(result=obj, clazz=clazz)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        all_classes = Clazz.objects.filter(grade__in=obj.grades.all())
        if obj.autofill:
            for clazz in all_classes:
                Placement.objects.get_or_create(result=obj, clazz=clazz)
        for placement in obj.placements.all():
            if placement.clazz not in all_classes and not placement.clazz.is_fake:
                placement.delete()
        return super().response_change(request, obj)
