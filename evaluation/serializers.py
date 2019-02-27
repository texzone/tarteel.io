from rest_framework import serializers
import evaluation.models


class TajweedEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = evaluation.models.TajweedEvaluation
        fields = '__all__'


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = evaluation.models.Evaluation
        fields = ('session_id', 'associated_recording', 'platform', "evaluation")
