from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('results', ResultsViewSet, basename='results')

urlpatterns = [
    path('', DisciplinesView.as_view(), name='disciplines'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category'),
] + router.urls + [
    path('<str:pk>/', DisciplineDetailView.as_view(), name='discipline'),
]