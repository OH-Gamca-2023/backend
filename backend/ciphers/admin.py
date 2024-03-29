import functools

from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path
from django_object_actions import DjangoObjectActions, action

from .models import *
from .views.admin import CipherOverviewView
from ..users.models import User


@admin.register(Cipher)
class CipherAdmin(DjangoObjectActions, admin.ModelAdmin):
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
                       'ignore_accents', 'submission_delay', 'max_submissions_per_day'),
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
                     'ignore_accents', 'submission_delay', 'max_submissions_per_day')

        return base

    @action()
    def results(self, request, queryset):
        individual_submitters = Submission.objects.filter(submitted_by__individual_cipher_solving=True).values_list(
            'submitted_by', flat=True).distinct()
        clazz_submitters = Submission.objects.filter(submitted_by__individual_cipher_solving=False).values_list(
            'clazz', flat=True).distinct()

        def get_results(submitters, individual):
            results = []
            for submitter in submitters:
                base_query = Submission.objects.filter(
                    submitted_by=submitter) if individual else Submission.objects.filter(clazz=submitter)
                result_obj = {
                    'submitter': User.objects.get(pk=submitter).username if individual else Clazz.objects.get(
                        pk=submitter).name,
                    'solved': base_query.filter(correct=True)
                    .values_list('cipher', flat=True).distinct(),
                    'days_until_solved': 0,
                    'solved_before_hint': base_query.filter(correct=True, after_hint=False)
                    .values_list('cipher', flat=True).distinct().count(),
                    'wrong': base_query.filter(correct=False).count(),
                    'time_until_solved': 0,
                    'individual': individual
                }

                for cipher in result_obj['solved']:
                    solving_submissions = base_query.filter(cipher=cipher, correct=True)
                    cipher = Cipher.objects.get(pk=cipher)
                    result_obj['days_until_solved'] += (
                                solving_submissions.order_by('time').first().time - cipher.start).days
                    result_obj['time_until_solved'] += int(
                        (solving_submissions.order_by('time').first().time - cipher.start).total_seconds())

                result_obj['solved'] = result_obj['solved'].count()
                results.append(result_obj)
            return results

        def sort_results(obj1, obj2):
            # higher is better: solved, solved_before_hint
            # lower is better: days_until_solved, wrong, time_until_solved
            if obj1['solved'] != obj2['solved']:
                return obj2['solved'] - obj1['solved']
            elif obj1['solved_before_hint'] != obj2['solved_before_hint']:
                return obj2['solved_before_hint'] - obj1['solved_before_hint']
            elif obj1['days_until_solved'] != obj2['days_until_solved']:
                return obj1['days_until_solved'] - obj2['days_until_solved']
            elif obj1['wrong'] != obj2['wrong']:
                return obj1['wrong'] - obj2['wrong']
            else:
                return obj1['time_until_solved'] - obj2['time_until_solved']

        results = get_results(individual_submitters, True) + get_results(clazz_submitters, False)
        results.sort(key=functools.cmp_to_key(sort_results))

        # generate csv
        csv = 'submitter,solved,solved_before_hint,days_until_solved,wrong,time_until_solved,individual\n'
        for result in results:
            csv += f'{result["submitter"]},{result["solved"]},{result["solved_before_hint"]},{result["days_until_solved"]},{result["wrong"]},{result["time_until_solved"]},{result["individual"]}\n'

        # return as csv attachment
        response = HttpResponse(csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="results.csv"'
        return response

    @action(label='Results and ratings')
    def results_and_ratings(self, request, obj):
        return redirect('admin:cipher_overview', pk=obj.pk)

    def get_urls(self):
        custom_urls = [
            path('<int:pk>/overview/', admin.site.admin_view(CipherOverviewView.as_view()),
                 name='cipher_overview')
        ]
        return custom_urls + super().get_urls()

    changelist_actions = ('results',)
    change_actions = ('results_and_ratings',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'clazz', 'cipher', 'answer', 'correct', 'after_hint', 'time', 'submitted_by', 'competing')
    list_filter = ('cipher', 'clazz', 'after_hint', 'correct')
    search_fields = ('answer',)
    ordering = ('-time',)
    autocomplete_fields = ('cipher', 'clazz', 'submitted_by')

    list_display_links = ('pk',)

    @admin.display(description='Súťažné', boolean=True)
    def competing(self, obj):
        return obj.clazz.grade.cipher_competing


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'submitter', 'cipher', 'stars', 'detail_cut', 'created', 'updated')
    list_filter = ('cipher', 'clazz')
    autocomplete_fields = ('cipher', 'clazz', 'submitted_by')
    ordering = ('-created',)

    list_display_links = ('pk', 'submitter')

    def detail_cut(self, obj):
        if obj.detail is None:
            return ''
        return obj.detail[:50] + '...' if len(obj.detail) > 50 else obj.detail
    detail_cut.short_description = 'Detail'


@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'rating', 'stars', 'detail_cut', 'created')
    list_filter = ('rating__cipher', 'rating__clazz')
    ordering = ('-created',)

    def detail_cut(self, obj):
        if obj.detail is None:
            return ''
        return obj.detail[:50] + '...' if len(obj.detail) > 50 else obj.detail
    detail_cut.short_description = 'Detail'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
