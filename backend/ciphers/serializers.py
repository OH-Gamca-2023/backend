from rest_framework import serializers
from rest_framework.reverse import reverse

from backend.ciphers.models import Cipher, Submission


class CipherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cipher
        fields = ['id', 'start', 'hint_publish_time', 'end', 'started', 'hint_visible', 'has_ended', 'submission_delay', 'max_submissions_per_day']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.started:
            ret['name'] = instance.name
            ret['task_file'] = reverse('ciphers:ciphers-task-file', kwargs={'pk': instance.pk})
            ret['task_file_ext'] = instance.task_file.name.split('.')[-1]
        if instance.hint_visible:
            ret['hint_text'] = instance.hint_text

        ret['data'] = None
        if self.context['request'].user.is_authenticated:

            clazz = self.context['request'].user.clazz
            if clazz.grade.cipher_competing:
                ret['data'] = {
                    'solved': instance.solved_by(clazz),
                    'after_hint': instance.solved_after_hint_by(clazz),
                    'attempts': instance.attempts_by(clazz)
                }
            else:
                ret['data'] = {
                    'solved': instance.solved_by(self.context['request'].user, True),
                    'after_hint': instance.solved_after_hint_by(self.context['request'].user, True),
                    'attempts': instance.attempts_by(self.context['request'].user, True)
                }
        return ret


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['submitted_by', 'cipher', 'clazz', 'time', 'after_hint', 'correct']

    def validate(self, data):
        data['cipher'] = Cipher.objects.get(pk=self.context['view'].kwargs['cipher_pk'])

        if data['cipher'].has_ended:
            raise serializers.ValidationError('This cipher has ended.')
        if not data['cipher'].started:
            raise serializers.ValidationError('This cipher has not started yet.')

        if self.context['request'].user.is_authenticated:
            if self.context['request'].user.clazz.grade.cipher_competing:
                if data['cipher'].solved_by(self.context['request'].user.clazz):
                    raise serializers.ValidationError('You have already solved this cipher.')
            else:
                if not self.context['request'].user.individual_cipher_solving:
                    raise serializers.ValidationError('You are not allowed to compete individually.')

                if data['cipher'].solved_by(self.context['request'].user, True):
                    raise serializers.ValidationError('You have already solved this cipher.')

            data['submitted_by'] = self.context['request'].user
            data['clazz'] = self.context['request'].user.clazz
        else:
            raise serializers.ValidationError('You must be logged in to submit answers.')

        data['correct'] = data['cipher'].validate_answer(data['answer'])
        data['after_hint'] = data['cipher'].hint_visible

        return data
