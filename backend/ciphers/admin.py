import functools

from django.contrib import admin, messages
from django.http import HttpResponse
from django_object_actions import DjangoObjectActions, action

from .models import *
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
        csv = 'submitter,solved,days_until_solved,solved_before_hint,wrong,time_until_solved,individual\n'
        for result in results:
            csv += f'{result["submitter"]},{result["solved"]},{result["days_until_solved"]},{result["solved_before_hint"]},{result["wrong"]},{result["time_until_solved"]},{result["individual"]}\n'

        # return as csv attachment
        response = HttpResponse(csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="results.csv"'
        return response

    changelist_actions = ('results',)


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
