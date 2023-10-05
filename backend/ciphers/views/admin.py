from django.contrib import admin
from django.views.generic import TemplateView

from backend.ciphers.models import Cipher, Rating, Submission
from backend.users.models import User, Clazz


class CipherOverviewView(TemplateView):
    template_name = 'admin/ciphers/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))

        context['opts'] = Cipher._meta
        context['cipher'] = Cipher.objects.get(pk=kwargs['pk'])
        if self.request.user.has_perm('ciphers.view_rating'):
            context['ratings'] = context['cipher'].rating_set.all()
        else:
            context['ratings_no_perm'] = True

        if self.request.user.has_perm('ciphers.view_submission'):
            context['results'] = self.get_results(context['cipher'])
        else:
            context['results_no_perm'] = True

        return context

    def get_results(self, cipher):
        individual_submitters = Submission.objects.filter(submitted_by__individual_cipher_solving=True).values_list(
            'submitted_by', flat=True).distinct()
        clazz_submitters = Submission.objects.filter(submitted_by__individual_cipher_solving=False).values_list(
            'clazz', flat=True).distinct()

        def submitter_results(submitters, individual):
            results = []
            for submitter in submitters:
                base_query = Submission.objects.filter(cipher=cipher,
                                                       submitted_by=submitter) if individual else \
                             Submission.objects.filter(cipher=cipher, clazz=submitter)

                result_obj = {
                    'submitter': f'Individual - {User.objects.get(pk=submitter).username}' if individual else
                                 f'Class - {Clazz.objects.get(pk=submitter).name}',
                    'attempts': base_query.count(),
                    'solved': base_query.filter(correct=True).exists(),
                    'solved_before_hint': base_query.filter(correct=True, after_hint=False).exists(),
                    'solved_at': base_query.filter(correct=True).order_by('time').first().time if base_query.filter(
                        correct=True).exists() else None,
                }
                results.append(result_obj)
            return results

        results = submitter_results(individual_submitters, True) + submitter_results(clazz_submitters, False)
        return results
