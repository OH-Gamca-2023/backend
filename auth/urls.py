from django.urls import path

from auth.views import *


urlpatterns = [
    path('callback/', callback, name='callback'),
    path('login/', sign_in, name='sign_in'),
    path('logout/', sign_out, name='sign_out'),
    path('invalidate/', invalidate, name='invalidate')
]