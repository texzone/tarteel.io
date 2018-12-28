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
        """Returns the last 10 recordings received."""
        recordings = AnnotatedRecording.objects.all().order_by('-timestamp')[:10]
        serializer = AnnotatedRecordingSerializerGet(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Creates a recording record in the DB using a serializer. Attempts
            to link a demographic if a session key exists.
        """
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
        print("Received recording data: {}".format(new_recording))
        if new_recording.is_valid(raise_exception=True):
            new_recording.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response("Invalid data, check the post request for all necessary data.",
                        status=status.HTTP_400_BAD_REQUEST)


class DemographicInformationViewList(APIView):
    """API endpoint that allows demographic information to be viewed or edited.
    """

    def get(self, request, format=None):
        recordings = DemographicInformation.objects.all().order_by('-timestamp')
        serializer = DemographicInformationSerializer(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        new_demographic = DemographicInformationSerializer(data=request.data)
        print("Received demographic data: {}".format(request.data))
        if new_demographic.is_valid(raise_exception=True):
            new_demographic.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response("Invalid data, check the post request for all necessary data.",
                        status=status.HTTP_400_BAD_REQUEST)


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
