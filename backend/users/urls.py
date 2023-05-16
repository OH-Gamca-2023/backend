from django.urls import path

from .views import *

urlpatterns = [
    path('me/', CurrentUserAPIView.as_view(), name='current_user'),
    path('me/password/', PasswordChangeAPIView.as_view(), name='change_password'),
    path('me/permissions/', UserPermissionAPIView.as_view(), name='user_permissions'),

    path('classes/', ClassesView.as_view(), name='classes'),
    path('classes/<int:pk>/', ClassDetailView.as_view(), name='class_detail'),

    path('grades/', GradesView.as_view(), name='grades'),
    path('grades/<int:pk>/', GradeDetailView.as_view(), name='grade_detail'),

    path('<int:pk>/', UserDetailAPIView.as_view(), name='user_detail'),
]