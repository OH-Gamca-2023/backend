from django.urls import path

from kalendar.views import *

urlpatterns = [
    path('json.json', json_default, name='JSON Calendar'),
    path('json_staff.json', json_staff, name='JSON Not published events'),
    path('json_all.json', json_all, name='JSON All events'),
    path('ical.ics', ical_default, name='ICAL Calendar'),
    path('ical_staff.ics', ical_staff, name='ICAL Not published events'),
    path('ical_all.ics', ical_all, name='JSON All events'),
]
