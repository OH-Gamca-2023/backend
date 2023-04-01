from django.urls import path

from users.views import *


urlpatterns = [
    path('me/', current_user, name='current_user'),
    path('me/password/', change_password, name='change_password'),
    path('me/permissions/', user_permissions, name='user_permissions'),
    path('classes/', classes, name='classes'),
    path('grades/', grades, name='grades'),
]