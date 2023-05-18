from django.utils import timezone
from rest_framework import serializers

from ciphers.models import Cipher, Submission


class CipherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cipher
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.context['request'].user.is_authenticated:
            ret['solved'] = instance.solved_by(self.context['request'].user.clazz)
            ret['solved_after_hint'] = instance.solved_after_hint_by(self.context['request'].user.clazz)
        return ret


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['submitted_by', 'clazz', 'time', 'after_hint', 'correct']

    def validate(self, data):
        if data['cipher'].has_ended or data['cipher'].end < timezone.now():
            raise serializers.ValidationError('This cipher has ended.')
        if not data['cipher'].visible:
            raise serializers.ValidationError('This cipher is not visible yet.')

        if self.context['request'].user.is_authenticated:
            if data['cipher'].solved_by(self.context['request'].user.clazz):
                raise serializers.ValidationError('You have already solved this cipher.')

            data['submitted_by'] = self.context['request'].user
            data['clazz'] = self.context['request'].user.clazz
        else:
            raise serializers.ValidationError('You must be logged in to submit answers.')

        data['correct'] = data['answer'].strip().lower() == data['cipher'].correct_answer.strip().lower()
        data['after_hint'] = data['cipher'].hint_visible

        return data
