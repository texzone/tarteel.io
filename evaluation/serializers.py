from rest_framework import serializers
import evaluation.models


class EvaluationSerializer(serializers.ModelSerializer):
  class Meta():
    model = evaluation.models.Evaluation
    fields = ('session_id', 'recording_id', 'platform', "evaluation")

