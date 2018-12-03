# Django
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms import modelformset_factory
from django.shortcuts import render
import json
import io
import os.path
from django.shortcuts import render
# Evaluation
from evaluation.serializers import EvaluationSerializer
from evaluation.models import Evaluation
from evaluation.models import TajweedEvaluation
from restapi.models import AnnotatedRecording

# RestAPI
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Python
import random

# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    evaluations = Evaluation.objects.all().count()
    # Get a random recording from the DB (Please don't use order_by('?')[0] :) )
    recording_ids = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
    random_recording = random.choice(recording_ids)
    # Load the Arabic Quran from JSON
    file_name = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        uthmani_quran = json.load(file)
        uthmani_quran = uthmani_quran["quran"]

    # Fields
    surah_num = random_recording.surah_num
    ayah_num = random_recording.ayah_num
    audio_url = random_recording.file.url
    ayah_text = uthmani_quran["surahs"][surah_num - 1]["ayahs"][ayah_num - 1]["text"]
    recording_id = random_recording.id

    # Create a form to have user input degree/category of mistake
    degree_cat_form = modelformset_factory(TajweedEvaluation,
                                           fields=('degree', 'category'))()
    context = {'degree_category_form': degree_cat_form,
               'surah_num': surah_num,
               'ayah_num': ayah_num,
               'ayah_text': ayah_text,
               'audio_url': audio_url,
               'recording_id': recording_id,
               "evaluations": evaluations
               }
    return render(request, 'evaluation/evaluator.html', context)


def tajweed_evluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    # Get a random recording from the DB (Please don't use order_by('?')[0] :) )
    recording_ids = list(AnnotatedRecording.objects.values_list('id', flat=True))
    random_id = random.choice(recording_ids)
    random_recording = AnnotatedRecording.objects.get(id=random_id)
    # Fields
    surah_num = random_recording.surah_num
    ayah_num = random_recording.ayah_num
    recitation_mode = random_recording.recitation_mode
    image_url = static('img/ayah_images/' + str(surah_num) + "_" + str(ayah_num) + '.png')
    audio_url = random_recording.file.url
    # Create a form to have user input degree/category of mistake
    TajweedEvaluationFormSet = modelformset_factory(TajweedEvaluation, fields=('degree', 'category'))
    degree_cat_form = TajweedEvaluationFormSet()

    return render(request, 'evaluation/tajweed_evaluator.html',
                  {'degree_category_form', degree_cat_form,
                   'surah_num', surah_num,
                   'ayah_num', ayah_num,
                   'recitation_mode', recitation_mode,
                   'image_url', image_url,
                   'audio_url', audio_url})


class TajweedEvaluationList(APIView):

    def post(self, request, *args, **kwargs):
        """Get """
        session_key = request.session.session_key or request.data["session_id"]
        return Response(status=status.HTTP_201_CREATED)


class EvaluationList(APIView):
    def get(self, request, *args, **kwargs):
        # Get a random recording from the DB (Please don't use order_by('?')[0] :) )
        recording_ids = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
        random_recording = random.choice(recording_ids)
        # Load the Arabic Quran from JSON
        file_name = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
        with io.open(file_name, 'r', encoding='utf-8-sig') as file:
            uthmani_quran = json.load(file)
            uthmani_quran = uthmani_quran["quran"]

        # Fields
        surah_num = random_recording.surah_num
        ayah_num = random_recording.ayah_num
        audio_url = random_recording.file.url
        ayah_text = uthmani_quran["surahs"][surah_num - 1]["ayahs"][ayah_num - 1]["text"]
        recording_id = random_recording.id
        res = {
            "audio_url": audio_url,
            "ayah_text": ayah_text,
            "recording_id": recording_id,
            "surah_num": surah_num,
            "ayah_num": ayah_num
        }
        return Response(res)

    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key or request.data["session_id"]
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

