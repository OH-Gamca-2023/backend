from django.contrib.admin.apps import AdminConfig


class OHGamcaAdminConfig(AdminConfig):
    default_site = 'admin.admin.OHGamcaAdminSite'