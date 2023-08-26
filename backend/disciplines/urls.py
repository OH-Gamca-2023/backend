from django.urls import path
from rest_framework.routers import SimpleRouter

from .views.api import *
from .views.sidebar import SidebarView

router = SimpleRouter()
router.register('results', ResultsViewSet, basename='results')
router.register('categories', CategoryViewSet, basename='categories')
router.register('', DisciplineViewSet, basename='disciplines')

urlpatterns = [
    path('sidebar', SidebarView.as_view(), name='sidebar'),
] + router.urls

app_name = 'backend.disciplines'