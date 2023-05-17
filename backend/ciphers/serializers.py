from rest_framework import serializers

from ciphers.models import Cipher, Submission


class CipherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cipher
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'