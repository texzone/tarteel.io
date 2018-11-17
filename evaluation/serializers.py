from rest_framework import serializers
from models import Evaluation

class EvaluationSerializer(serializers.ModelSerializer):
  class Meta():
    model = Evaluation
    fields = ('session_id', 'recording_id', 'platform', "evaluation")

