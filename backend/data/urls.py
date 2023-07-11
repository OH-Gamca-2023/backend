from rest_framework.routers import SimpleRouter

from backend.data.views import AlertViewSet, SettingViewSet

router = SimpleRouter()
router.register('alerts', AlertViewSet, basename='alerts')
router.register('settings', SettingViewSet, basename='settings')
urlpatterns = router.urls

app_name = 'backend.data'