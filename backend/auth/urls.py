from django.urls import path

from .views import *

from knox import views as knox_views

urlpatterns = [
    path('callback/', OauthCallbackView.as_view(), name='callback'),
    path('login/', OauthStartView.as_view(), name='sign_in'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('admin/login/', OauthAdminStartView.as_view(), name='admin_sign_in'),
    path('admin/callback/', OauthAdminCallbackView.as_view(), name='admin_callback'),
]

app_name = 'backend.auth'
