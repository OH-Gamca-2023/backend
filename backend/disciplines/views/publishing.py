from django.contrib import admin, messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic.edit import CreateView

from backend.disciplines.models import Discipline
from backend.posts.admin import TagAdmin
from backend.posts.models import Post, Tag


class PublishView(PermissionRequiredMixin, CreateView):
    permission_required = None
    template_name = 'admin/disciplines/publish.html'
    action = None
    readable_action = None

    special_tags = []

    model = Post
    fields = ['title', 'redirect', 'related_disciplines', 'affected_grades', 'tags']
    fieldsets = [
        ("Názov príspevku", {
            'description': 'Názov príspevku ktorý sa zobrazí na stránke.<br>'
                           '<i>Presmerovanie nemeňte, ak nie ste admin jeho zmena bude ignorovaná.</i>',
            'fields': ['title', 'redirect']
        }),
        ("Dodatočné údaje", {
            'description': 'Tieto údaje pravdepodobne netreba meniť',
            'fields': [('related_disciplines', 'affected_grades', 'tags')]
        })
    ]

    def get_success_url(self):
        return reverse('admin:disciplines_discipline_change', args=[self.kwargs['discipline_id']])

    def get_discipline(self):
        return Discipline.objects.get(id=self.kwargs['discipline_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))

        context['discipline'] = self.get_discipline()
        context['action'] = self.readable_action
        context['opts'] = Discipline._meta
        context['title'] = f'{self.readable_action} - {context["discipline"].name}'

        context['adminform'] = admin.helpers.AdminForm(self.get_form(), self.fieldsets, {})

        return context

    def get_default_title(self, discipline):
        return f'Error: get_default_title() not implemented for {self.__class__.__name__}'

    def get_default_redirect_url(self, discipline):
        return f'Error: get_default_redirect_url() not implemented for {self.__class__.__name__}'

    def get_initial(self):
        default = {
            'title': self.get_default_title(self.get_discipline()),
            'redirect': self.get_default_redirect_url(self.get_discipline()),
            'related_disciplines': [self.get_discipline().id],
            'affected_grades': [grade.id for grade in self.get_discipline().target_grades.all()],
            'tags': []
        }

        TagAdmin.create_default_tags(None, self.request, None)
        for tag in self.special_tags:
            if Tag.objects.filter(special=tag).exists():
                default['tags'].append(Tag.objects.get(special=tag).id)
        return default

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method in ("POST", "PUT"):
            # enable modifying QueryDict
            kwargs['data']._mutable = True

            # add missing related_disciplines, affected_grades and tags from initial to data
            for field in ['related_disciplines', 'affected_grades', 'tags']:
                if field not in kwargs['data']:
                    kwargs['data'].setlist(field, kwargs['initial'][field])
                else:
                    for val in kwargs['initial'][field]:
                        if str(val) not in kwargs['data'].getlist(field):
                            kwargs['data'].appendlist(field, str(val))

            # reset redirect to initial value if not superuser
            if not self.request.user.is_superuser:
                kwargs['data']['redirect'] = kwargs['initial']['redirect']

            # disable modifying QueryDict
            kwargs['data']._mutable = False

        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # set {type}_published on discipline to True
        discipline = self.get_discipline()
        setattr(discipline, f'{self.action}_published', True)
        discipline.save()

        # add alert to user
        messages.success(self.request, f'{self.readable_action} pre {discipline.name} bolo úspešne dokončené')

        return response


class DetailsPublishView(PublishView):
    permission_required = 'disciplines.publish_details'
    action = 'details'
    readable_action = 'Zverejnenie detailov'

    special_tags = ['info']

    def get_default_title(self, discipline):
        return f'{discipline.name}'

    def get_default_redirect_url(self, discipline):
        return f'/discipline/{discipline.id}'


class ResultsPublishView(PublishView):
    permission_required = 'disciplines.publish_results'
    action = 'results'
    readable_action = 'Zverejnenie výsledkov'

    special_tags = ['results']

    def get_default_title(self, discipline):
        return f'Výsledky {discipline.name}'

    def get_default_redirect_url(self, discipline):
        return f'/discipline/{discipline.id}/results'
