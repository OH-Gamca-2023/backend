from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('classes', ClassViewSet, basename='classes')
router.register('grades', GradeViewSet, basename='grades')
router.register('', UserViewSet, basename='users')

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('me/password/', PasswordChangeView.as_view(), name='change_password'),
    path('me/permissions/', CurrentUserPermissionView.as_view(), name='user_permissions'),
] + router.urls

app_name = 'backend.users'