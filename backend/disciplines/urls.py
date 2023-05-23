from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('results', ResultsViewSet, basename='results')
router.register('categories', CategoryViewSet, basename='categories')
router.register('', DisciplineViewSet, basename='disciplines')

urlpatterns = router.urls