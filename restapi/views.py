# Django
from django.contrib.auth.models import User, Group
# REST
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
# Tarteel
from restapi.serializers import UserSerializer, GroupSerializer, \
    AnnotatedRecordingSerializerPost, AnnotatedRecordingSerializerGet, \
    DemographicInformationSerializer
from restapi.models import AnnotatedRecording, DemographicInformation


class AnnotatedRecordingList(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, format=None):
        recordings = AnnotatedRecording.objects.all().order_by('-timestamp')[:10]
        serializer = AnnotatedRecordingSerializerGet(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Check if session key exists
        session_key = request.session.session_key or request.data["session_id"]
        request.data['session_id'] = session_key
        # Check if demographic with key exists (default to None)
        # TODO(piraka9011): Associate with user login once auth is developed.
        request.data['associated_demographic'] = None
        demographic = DemographicInformation.objects.filter(session_id=session_key).order_by('-timestamp')
        if demographic.exists():
            request.data['associated_demographic'] = demographic[0].id
        new_recording = AnnotatedRecordingSerializerPost(data=request.data)
        print(new_recording)
        if not (new_recording.is_valid()):
            raise ValueError("Invalid serializer data")
        try:
            # TODO(abidlabs): I don't think these next two lines are necessary.
            #  Confirm and delete if not necessary.
            new_recording.file = request.data['file']
            new_recording.session_id = session_key
            new_recording.save()
        except:
            return Response("Invalid hash or timed out request",
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class DemographicInformationViewList(APIView):
    """API endpoint that allows demographic information to be viewed or edited.
    """

    def get(self, request, format=None):
        recordings = DemographicInformation.objects.all().order_by('-timestamp')
        serializer = DemographicInformationSerializer(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key or request.data["session_id"]
        new_entry = DemographicInformationSerializer(data=request.data)
        new_entry.is_valid(raise_exception=True)
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
            return Response("Invalid request",
                            status=status.HTTP_400_BAD_REQUEST)
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
        recording_count = AnnotatedRecording.objects.filter(file__gt='',
                                                            file__isnull=False).count()

        return Response({"count": recording_count})
