from django.contrib.auth.models import User, Group
from rest_framework import serializers
from restapi.models import AnnotatedRecording, DemographicInformation

class AnnotatedRecordingSerializerPost(serializers.ModelSerializer):
  class Meta():
    model = AnnotatedRecording
    fields = ('file', 'hash_string', 'surah_num', 'ayah_num', 'timestamp', 'recitation_mode')

class AnnotatedRecordingSerializerGet(serializers.ModelSerializer):
  class Meta():
    model = AnnotatedRecording
    fields = ('file', 'hash_string', 'surah_num', 'ayah_num', 'timestamp', 'session_id', 'recitation_mode')

class DemographicInformationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta():
        model = DemographicInformation
        fields = ('session_id', 'platform', 'gender', 'age', 'ethnicity', 'country', 'timestamp', 'qiraah')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
