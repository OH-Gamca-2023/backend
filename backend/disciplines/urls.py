from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register('results', ResultsViewSet, basename='results')
router.register('categories', CategoryViewSet, basename='categories')
router.register('', DisciplineViewSet, basename='disciplines')

urlpatterns = router.urls
