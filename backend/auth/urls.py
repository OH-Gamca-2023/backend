from django.urls import path

from .views import *

from knox import views as knox_views

urlpatterns = [
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),

    path('login/', LoginView.as_view(), name='basic_login'),

    path('begin/<str:service>/', OauthStartView.as_view(), name='oauth_begin'),
    path('callback/<str:service>/', OauthCallbackView.as_view(), name='oauth_callback'),
    path('verify/<str:service>/', OauthVerifyView.as_view(), name='oauth_verify'),

]

app_name = 'backend.auth'
