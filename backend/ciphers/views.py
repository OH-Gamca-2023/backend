from django.utils import timezone
from rest_framework import permissions, viewsets, throttling

from backend import settings
from backend.utils import ReadCreateViewSet
from ciphers.models import Cipher, Submission
from ciphers.serializers import CipherSerializer, SubmissionSerializer


class CiphersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cipher.objects.filter()
    serializer_class = CipherSerializer


class SubmissionRateThrottle(throttling.BaseThrottle):

    def allow_request(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'POST':
                cipher_pk = view.kwargs['cipher_pk']
                last_submission = Submission.objects.filter(clazz=request.user.clazz,
                                                            cipher_id=cipher_pk).order_by('-time').first()
                if last_submission is not None and last_submission.time + settings.CIPHERS_DELAY > timezone.now():
                    return False
        return True

    def wait(self):
        return settings.CIPHERS_DELAY.total_seconds()


class SubmissionViewSet(ReadCreateViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SubmissionRateThrottle]

    def get_queryset(self):
        base = Submission.objects.filter(cipher=self.kwargs['cipher_pk'])
        if self.request.user.is_authenticated:
            return base.filter(clazz=self.request.user.clazz)
        return base.none()

