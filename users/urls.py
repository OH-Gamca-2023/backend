from django.urls import path

from users.views import *


urlpatterns = [
    path('me/', current_user, name='current_user'),
    path('classes/', classes, name='classes'),
    path('grades/', grades, name='grades'),
]