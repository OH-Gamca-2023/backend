from django.utils import timezone
from rest_framework import permissions, viewsets, throttling

from backend.utils import ReadCreateViewSet
from ciphers.models import Cipher, Submission
from ciphers.serializers import CipherSerializer, SubmissionSerializer


class CiphersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cipher.objects.filter(visible=True)
    serializer_class = CipherSerializer


class SubmissionRateThrottle(throttling.BaseThrottle):
    DELAY = timezone.timedelta(minutes=10)

    def allow_request(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'POST':
                last_submission = Submission.objects.filter(clazz=request.user.clazz,
                                                            cipher=request.data['cipher']).order_by('-time').first()
                if last_submission is not None and last_submission.time + self.DELAY > timezone.now():
                    return False
        return True

    def wait(self):
        return self.DELAY.total_seconds()


class SubmissionViewSet(ReadCreateViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SubmissionRateThrottle]

    def get_queryset(self):
        base = Submission.objects.filter(cipher=self.kwargs['cipher_pk'])
        if self.request.user.is_authenticated:
            return base.filter(clazz=self.request.user.clazz)
        return base.none()

