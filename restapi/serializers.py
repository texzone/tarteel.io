from django.contrib.auth.models import User, Group
from rest_framework import serializers
from restapi.models import AnnotatedRecording, DemographicInformation


class AnnotatedRecordingSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = AnnotatedRecording
        fields = ('file', 'hash_string', 'surah_num', 'ayah_num', 'timestamp',
                  'recitation_mode', 'associated_demographic', 'session_id')


class DemographicInformationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DemographicInformation
        fields = ('session_id', 'platform', 'gender', 'age', 'ethnicity',
                  'country', 'timestamp', 'qiraah')


class AnnotatedRecordingSerializerGet(serializers.ModelSerializer):
    associated_demographic = DemographicInformationSerializer()

    class Meta:
        model = AnnotatedRecording
        fields = ('file', 'hash_string', 'surah_num', 'ayah_num', 'timestamp',
                  'session_id', 'recitation_mode', 'associated_demographic')


class AnnotatedRecordingSerializer(serializers.ModelSerializer):
    associated_demographic = DemographicInformationSerializer()

    class Meta:
        model = AnnotatedRecording
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
