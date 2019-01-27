# Global
from os.path import join, dirname, abspath
import random
import io
import json
import datetime
from collections import defaultdict
import os
# Django
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django_filters import rest_framework as filters
from django.db.models import Count
# REST
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
# Tarteel
from restapi.serializers import UserSerializer, GroupSerializer, \
    AnnotatedRecordingSerializerPost, AnnotatedRecordingSerializerGet, \
    DemographicInformationSerializer, AnnotatedRecordingSerializer
from restapi.models import AnnotatedRecording, DemographicInformation
from audio.views import get_low_ayah_count, _sort_recitations_dict_into_lists
from evaluation.models import Evaluation
from evaluation.serializers import EvaluationSerializer

# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(abspath(__file__)))
INT_NA_VALUE = -1
STRING_NA_VALUE = "N/A"

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


class AnnotatedRecordingFilter(filters.FilterSet):
    surah = filters.NumberFilter(field_name='surah_num')
    ayah = filters.NumberFilter(field_name='ayah_num')
    gender = filters.CharFilter(field_name='associated_demographic__gender')

    class Meta:
        model = AnnotatedRecording
        fields = ['gender', 'surah', 'ayah']


class AnnotatedRecordingViewSet(viewsets.ModelViewSet):
    """API to handle query parameters
    Example: api/v1/recordings/?surah=114&ayah=1
    """
    serializer_class = AnnotatedRecordingSerializer
    queryset = AnnotatedRecording.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnnotatedRecordingFilter


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


class GetAyah(APIView):
    """Gets the surah num, ayah num, and text of an ayah of a specified maximum length."""

    def get(self, request, format=None):
        """Gets the surah num, ayah num, and text of an ayah of a specified maximum length.

        :param request: rest API request object.
        :type request: Request
        :param line_length: The maximum number of characters in an ayah.
        :return: A JSON response with the surah/ayah numbers, text, hash, ID, and image.
        :rtype: JsonResponse
        """
        # User tracking - Ensure there is always a session key.
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        line_length = request.GET.get('line_length') or 200

        # Load the Arabic Quran from JSON
        file_name = join(BASE_DIR, 'utils/data-words.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            quran = json.load(file)
            file.close()

        # Load the Arabic Quran from JSON
        file_name = join(BASE_DIR, 'utils/data-uthmani.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            quran_uthmani = json.load(file)
            file.close()

        surah, ayah, line = get_low_ayah_count(quran_uthmani, line_length)
        ayah = quran[str(surah)]["verses"][int(ayah) - 1]

        # Set image file and hash
        # image_url = static('img/ayah_images/' + str(surah) + "_" + str(ayah) + '.png')
        req_hash = random.getrandbits(32)

        # Format as json, and save row in DB

        ayah['hash'] = req_hash
        ayah['session_id'] = session_key

        return Response(ayah)

    def post(self, request, *args, **kwargs):

        # User tracking - Ensure there is always a session key.
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # Load the Arabic Quran from JSON
        file_name = join(BASE_DIR, 'utils/data-words.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            quran = json.load(file)
            file.close()

        surah = str(request.data['surah'])
        ayah = int(request.data['ayah'])
        # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
        ayah = quran[surah]["verses"][ayah - 1]

        # Set image file and hash
        # image_url = static('img/ayah_images/' + str(surah) + "_" + str(ayah) + '.png')
        req_hash = random.getrandbits(32)

        # Format as json, and save row in DB

        ayah['hash'] = req_hash
        ayah['session_id'] = session_key

        return Response(ayah)


class GetSurah(APIView):
    """Gets all the ayahs in specific surah given by num"""

    def get(self, request, num, format=None):
        """Returns the ayahs of specific surah.

        :param request: rest API request object.
        :type request: Request
        :num param: the surah number
        :return: A JSON response with the requested text.
        :rtype: JsonResponse
        """
        # Load the Transliteration Quran from JSON
        file_name = join(BASE_DIR, 'utils/data.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            ayahs = json.load(file)
            file.close()

        surah = num
        ayah_list = ayahs[surah]

        res = {
            'chapter_id': num,
            'ayahs': ayah_list,
        }

        return Response(res)


class Index(APIView):

    def get(self, request, format=None):
        """ Gets today's and total recording counts as well as checks
        for whether we have demographic info for the session.

        :param request: rest API request object.
        :type request: Request
        :return: HttpResponse with total number of recordings, today's recordings, and a check
        to ask for demographic info.
        :rtype: HttpResponse
        """
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).count()
        evaluations = Evaluation.objects.all().count()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        # Check if we need demographics for this session
        ask_for_demographics = DemographicInformation.objects.filter(session_id=session_key).exists()

        daily_count = AnnotatedRecording.objects.filter(
            file__gt='', timestamp__gt=yesterday).exclude(file__isnull=True).count()
        return Response({
            'recording_count': recording_count,
            'daily_count': daily_count,
            'evaluations_count': evaluations,
            'session_key': session_key,
            'ask_for_demographics': ask_for_demographics
        })



class About(APIView):
    """ Gets the required data for About page Includes queries for graphs."""

    def get(self, request):
        """ Gets the required data for About page Includes queries for graphs.

        :param request: rest API request object.
        :type request: Request
        :return: HttpResponse with total number of recordings and labels for graphs
        :rtype: HttpResponse
        """
        session_key = request.session.session_key
        # Number of recordings
        recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).count()
        user_recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False, session_id=session_key).count()
        unique_user_count = DemographicInformation.objects.count()

        # Demographic data for the graphs.
        # Gender
        gender_labels = ['male', 'female']
        gender_counts = DemographicInformation.objects.filter(
            gender__in=gender_labels).values('gender').annotate(
            the_count=Count('gender'))
        gender_labels = [k['gender'] for k in gender_counts]
        gender_data = [k['the_count'] for k in gender_counts]

        # Age
        age_labels = ['13', '19', '26', '36', '46', '56']
        age_counts = DemographicInformation.objects.filter(
            age__in=age_labels).values('age').annotate(
            the_count=Count('age'))
        age_labels = [k['age'] for k in age_counts]
        age_label_map = {'13': '13-18',
                         '19': '19-25',
                         '26': '26-35',
                         '36': '36-45',
                         '46': '46-55',
                         '56': '56+'}
        age_labels = [age_label_map[a] for a in age_labels]
        age_data = [k['the_count'] for k in age_counts]

        # Ethnicity
        ethnicity_counts = DemographicInformation.objects.values(
            'ethnicity').annotate(the_count=Count('ethnicity')).order_by(
            '-the_count')[:6]
        ethnicity_labels = [k['ethnicity'] for k in ethnicity_counts]
        ethnicity_data = [k['the_count'] for k in ethnicity_counts]

        # Get ayah data for the graphs.
        ayah_counts = list(AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).values(
            'surah_num', 'ayah_num').annotate(count=Count('pk')))
        raw_counts = [ayah['count'] for ayah in ayah_counts]
        count_labels = ['0', '1', '2', '3', '4', '5+']
        # noinspection PyListCreation
        count_data = [
            TOTAL_AYAH_NUM - len(ayah_counts),  # ayahs not in list have 0 count
            raw_counts.count(1),
            raw_counts.count(2),
            raw_counts.count(3),
            raw_counts.count(4)]
        count_data.append(TOTAL_AYAH_NUM - sum(count_data))  # remaining have 5+ count

        recording_count_formatted = "{:,}".format(recording_count)  # Add commas to this number as it is used for display.

        return Response({
            'recording_count': recording_count,
            'recording_count_formatted': recording_count_formatted,
            'gender_labels': gender_labels,
            'gender_data': gender_data,
            'unique_user_count': unique_user_count,
            'user_recording_count': user_recording_count,
            'age_labels': age_labels,
            'age_data': age_data,
            'count_labels': count_labels,
            'count_data': count_data,
            'session_key': session_key,
            'ethnicity_labels': ethnicity_labels,
            'ethnicity_data': ethnicity_data
        })


class Profile(APIView):

    def get(self, request, session_key):
        """ Returns the session profile data.

         :param request: rest API request object.
         :type request: Request
         :param session_key: string representing the session key for the user
         :type session_key: str
         :return: Just another django mambo.
         :rtype: HttpResponse
         """
        my_session_key = request.session.session_key  # This may be different from the one provided in the URL.
        last_week = datetime.date.today() - datetime.timedelta(days=7)

        # Get the weekly counts.
        last_weeks = [datetime.date.today() - datetime.timedelta(days=days) for days in [6, 13, 20, 27, 34]]
        dates = []
        weekly_counts = []
        for week in last_weeks:
            dates.append(week.strftime('%m/%d/%Y'))
            count = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False, session_id=session_key, timestamp__gt=week,
                timestamp__lt=week + datetime.timedelta(days=7)).count()
            weekly_counts.append(count)

        recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).count()

        # Construct dictionaries of the user's recordings.
        user_recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False, session_id=session_key).count()
        recent_recordings = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False, session_id=session_key, timestamp__gt=last_week)
        recent_dict = defaultdict(list)
        [recent_dict[rec.surah_num].append((rec.ayah_num, rec.file.url)) for rec in recent_recordings]
        old_recordings = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False, session_id=session_key, timestamp__lt=last_week)
        old_dict = defaultdict(list)
        [old_dict[rec.surah_num].append((rec.ayah_num, rec.file.url)) for rec in old_recordings]

        recent_lists = _sort_recitations_dict_into_lists(recent_dict)
        old_lists = _sort_recitations_dict_into_lists(old_dict)

        return Response({
            'session_key': my_session_key,
            'recent_dict': dict(recent_dict),
            'recent_lists': recent_lists,
            'old_lists': old_lists,
            'dates': dates[::-1],
            'weekly_counts': weekly_counts[::-1],
            'old_dict': dict(old_dict),
            'recording_count': recording_count,
            'user_recording_count': user_recording_count
        })


class EvaluationList(APIView):
    def get(self, request, *args, **kwargs):
        # Get a random recording from the DB (Please don't use order_by('?')[0] :) )
        recording_ids = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
        random_recording = random.choice(recording_ids)
        # Load the Arabic Quran from JSON
        file_name = os.path.join(BASE_DIR, 'utils/data-words.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            uthmani_quran = json.load(file)

        # Fields
        surah_num = str(random_recording.surah_num)
        ayah_num = random_recording.ayah_num
        audio_url = random_recording.file.url
        ayah = uthmani_quran[surah_num]["verses"][ayah_num - 1]
        recording_id = random_recording.id
        print(recording_id)

        ayah["audio_url"] = audio_url
        ayah["recording_id"]: recording_id

        return Response(ayah)

    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key
        data = {
            "session_id": session_key
        }
        ayah = request.data["ayah"]
        data["recording_id"] = ayah["recording_id"]
        data["evaluation"] = ayah["evaluation"]
        new_evaluation = EvaluationSerializer(data=data)

        if not(new_evaluation.is_valid()):
            raise ValueError("Invalid serializer data")
        try:
            new_evaluation.save()
        except:
            return Response("Invalid hash or timed out request", status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

