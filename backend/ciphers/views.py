from django.http import FileResponse
from django.utils import timezone
from rest_framework import permissions, viewsets, throttling
from rest_framework.decorators import action

from backend.users.utils import ReadCreateViewSet
from backend.ciphers.models import Cipher, Submission
from backend.ciphers.serializers import CipherSerializer, SubmissionSerializer


class CiphersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cipher.objects.filter()
    serializer_class = CipherSerializer

    @action(detail=True, methods=['get'], url_path='task')
    def task_file(self, request, pk=None):
        cipher = self.get_object()
        hex, ext = cipher.task_file.name.split('/')[-1].split('.')
        cipher_name = cipher.name.replace(' ', '_')
        return FileResponse(cipher.task_file, as_attachment=False, filename=f'{cipher_name}_zadanie_{hex[:5]}.{ext}')


class SubmissionRateThrottle(throttling.BaseThrottle):

    def allow_request(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'POST':
                cipher_pk = view.kwargs['cipher_pk']

                base = None

                if request.user.clazz.grade.cipher_competing:
                    base = Submission.objects.filter(clazz=request.user.clazz)
                else:
                    base = Submission.objects.filter(submitted_by=request.user)

                cipher = Cipher.objects.get(pk=cipher_pk)

                if base.filter(cipher_id=cipher_pk, time__day=timezone.now().day).count() >= cipher.max_submissions_per_day:
                    return False

                last_submission = base.filter(clazz=request.user.clazz, cipher_id=cipher_pk).order_by('-time').first()

                submission_delay = cipher.submission_delay
                if not request.user.clazz.grade.cipher_competing:
                    submission_delay *= 2

                if last_submission and last_submission.time + timezone.timedelta(seconds=submission_delay) > timezone.now():
                    return False
        return True


class SubmissionViewSet(ReadCreateViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SubmissionRateThrottle]

    def get_queryset(self):
        base = Submission.objects.filter(cipher=self.kwargs['cipher_pk'])
        if self.request.user.is_authenticated:
            if self.request.user.clazz.grade.cipher_competing:
                return base.filter(clazz=self.request.user.clazz)
            else:
                return base.filter(submitted_by=self.request.user)
        return base.none()