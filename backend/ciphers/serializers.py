from rest_framework import serializers

from ciphers.models import Cipher, Submission
from users.models import Clazz


class CipherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cipher
        fields = ['id', 'start', 'hint_publish_time', 'end', 'started', 'hint_visible', 'has_ended', 'submission_delay']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.started:
            ret['name'] = instance.name
            ret['task_file'] = instance.task_file.url
        if instance.hint_visible:
            ret['hint_text'] = instance.hint_text

        ret['classes'] = {}
        if self.context['request'].user.is_authenticated:
            if self.context['request'].user.is_staff:
                for clazz in Clazz.objects.filter(grade__cipher_competing=True):
                    ret['classes'][clazz.id] = {
                        'solved': instance.solved_by(clazz),
                        'after_hint': instance.solved_after_hint_by(clazz),
                        'attempts': instance.attempts_by(clazz)
                    }

            clazz = self.context['request'].user.clazz
            if clazz.grade.cipher_competing:
                ret['classes'][clazz.id] = {
                    'solved': instance.solved_by(clazz),
                    'after_hint': instance.solved_after_hint_by(clazz),
                    'attempts': instance.attempts_by(clazz)
                }
            else:
                ret['classes'][clazz.id] = {
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
                if data['cipher'].solved_by(self.context['request'].user, True):
                    raise serializers.ValidationError('You have already solved this cipher.')

            data['submitted_by'] = self.context['request'].user
            data['clazz'] = self.context['request'].user.clazz
        else:
            raise serializers.ValidationError('You must be logged in to submit answers.')

        data['correct'] = data['answer'].strip().lower() == data['cipher'].correct_answer.strip().lower()
        data['after_hint'] = data['cipher'].hint_visible

        return data
