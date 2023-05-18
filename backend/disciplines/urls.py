from django.urls import path

from .views import *

urlpatterns = [
    path('', DisciplinesView.as_view(), name='disciplines'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category'),
    path('<str:pk>/', DisciplineDetailView.as_view(), name='discipline'),
]
