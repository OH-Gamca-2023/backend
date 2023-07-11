from rest_framework.routers import SimpleRouter

from backend.ciphers.views import CiphersViewSet, SubmissionViewSet

router = SimpleRouter()
router.register('', CiphersViewSet, basename='ciphers')
router.register(r'(?P<cipher_pk>\d+)/submissions', SubmissionViewSet, basename='cipher_submissions')
urlpatterns = router.urls

app_name = 'backend.ciphers'