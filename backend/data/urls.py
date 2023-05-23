from rest_framework.routers import SimpleRouter

from data.views import AlertViewSet, SettingViewSet

router = SimpleRouter()
router.register('alerts', AlertViewSet, basename='alerts')
router.register('settings', SettingViewSet, basename='settings')
urlpatterns = router.urls