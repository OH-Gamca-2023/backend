from django.urls import path

from .views import *

urlpatterns = [
    path('', DisciplineListApiView.as_view(), name='disciplines'),
    path('categories/', CategoriesListApiView.as_view(), name='categories'),
    path('<str:id>/', DisciplineApiView.as_view(), name='discipline'),
]
