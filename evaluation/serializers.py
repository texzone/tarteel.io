from rest_framework import serializers
from evaluation.models import TajweedEvaluation


class TajweedEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TajweedEvaluation
        fields = ('recording_id', 'platform', 'letter', 'letter_position',
                  'degree', 'category')
