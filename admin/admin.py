from django.contrib import admin, messages
from django.db.models import Q
from django.utils import timezone

from backend.data.models import Alert


class OHGamcaAdminSite(admin.AdminSite):
    login_template = 'admin/login.html'

    def each_context(self, request):
        alerts = Alert.objects.filter(show_in_admin=True, active=True)\
            .filter(Q(lasts_until__isnull=True) | Q(lasts_until__gte=timezone.now()))
        for alert in alerts:
            messages.add_message(request, alert.get_django_level(), alert.message)
        return super().each_context(request)
