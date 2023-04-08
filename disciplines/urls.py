from django.urls import path

from disciplines.views import categories


urlpatterns = [
    path('categories/', categories, name='categories'),
]
