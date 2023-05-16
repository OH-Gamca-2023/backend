from django.urls import path

from .views import *

urlpatterns = [
    path('me/', CurrentUserAPIView.as_view(), name='current_user'),
    path('me/password/', PasswordChangeAPIView.as_view(), name='change_password'),
    path('me/permissions/', UserPermissionAPIView.as_view(), name='user_permissions'),

    path('classes/', ClassListAPIView.as_view(), name='classes'),
    path('classes/<int:pk>/', ClassDetailAPIView.as_view(), name='class_detail'),

    path('grades/', GradeListAPIView.as_view(), name='grades'),
    path('grades/<int:pk>/', GradeDetailAPIView.as_view(), name='grade_detail'),
]