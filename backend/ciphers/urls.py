
from rest_framework.routers import DefaultRouter

from ciphers.views import CiphersViewSet, SubmissionViewSet

router = DefaultRouter()
router.register('', CiphersViewSet, basename='ciphers')
router.register(r'(?P<cipher_pk>\d+)/submissions', SubmissionViewSet, basename='cipher_submissions')
urlpatterns = router.urls