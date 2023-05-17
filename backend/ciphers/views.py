from rest_framework import permissions, generics, viewsets

from backend.utils import ReadCreateViewSet
from ciphers.models import Cipher, Submission
from ciphers.serializers import CipherSerializer, SubmissionSerializer


class CiphersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cipher.objects.filter(visible=True)
    serializer_class = CipherSerializer


class SubmissionViewSet(ReadCreateViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        base = Submission.objects.filter(cipher=self.kwargs['cipher_pk'])
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return base
            return base.filter(clazz=self.request.user.clazz)

