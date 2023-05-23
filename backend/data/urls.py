from rest_framework.routers import DefaultRouter

from data.views import AlertViewSet, SettingViewSet

router = DefaultRouter()
router.register('alerts', AlertViewSet, basename='alerts')
router.register('settings', SettingViewSet, basename='settings')
urlpatterns = router.urls