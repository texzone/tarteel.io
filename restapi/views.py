from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from rest_framework import viewsets
from restapi.serializers import UserSerializer, GroupSerializer, AnnotatedRecordingSerializerPost, AnnotatedRecordingSerializerGet, DemographicInformationSerializer
from restapi.models import AnnotatedRecording, DemographicInformation
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import permissions


class AnnotatedRecordingList(APIView):
  parser_classes = (MultiPartParser, FormParser)

  # def get(self, request, format=None):
  #     recordings = AnnotatedRecording.objects.all().order_by('-timestamp')[:100]
  #     serializer = AnnotatedRecordingSerializerGet(recordings, many=True)
  #     return Response(serializer.data)

  def post(self, request, *args, **kwargs):
    session_key = request.session.session_key or request.data["session_id"]
    print("request.data", request.data)
    new_recording = AnnotatedRecordingSerializerPost(data=request.data)
    if not(new_recording.is_valid()):
      raise ValueError("Invalid serializer data")
    try:
        # existing_recording = AnnotatedRecording.objects.get(
        #   hash_string=new_recording.data['hash_string'],
        #   ayah_num=new_recording.data['ayah_num'],
        #   surah_num=new_recording.data['surah_num'])
        # existing_recording.file = request.data['file']
        # existing_recording.session_id = session_key
        # existing_recording.save()
        new_recording.file = request.data['file']
        new_recording.session_id = session_key
        new_recording.save()
    except:
      return Response("Invalid hash or timed out request", status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)


class DemographicInformationViewList(APIView):
  """
  API endpoint that allows demographic information to be viewed or edited.
  """
  def get(self, request, format=None):
    recordings = DemographicInformation.objects.all().order_by('-timestamp')
    serializer = DemographicInformationSerializer(recordings, many=True)
    return Response(serializer.data)

  def post(self, request, *args, **kwargs):
    session_key = request.session.session_key or request.data["session_id"]
    new_entry = DemographicInformationSerializer(data=request.data)
    if not(new_entry.is_valid()):
      raise ValueError("Invalid serializer data")
    try:
      new_entry = DemographicInformation.objects.create(
          session_id=session_key,
          gender=new_entry.data.get('gender'),
          age=new_entry.data.get('age'),
          ethnicity=new_entry.data.get('ethnicity'),
          qiraah=new_entry.data.get('qiraah'),
          country=new_entry.data.get('country')
        )
    except:
      return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class RecordingsCount(APIView):
    """
    API endpoint that gets the total count of the recording files 
    """

    def get(self, request, format=None):
        recording_count = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False).count()

        return Response({"count": recording_count})
