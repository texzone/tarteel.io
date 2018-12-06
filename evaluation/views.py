# -*- coding: utf-8 -*-
# Django
from django.forms import modelformset_factory
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# REST
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
# Tarteel
from evaluation.models import TajweedEvaluation
from evaluation.serializers import TajweedEvaluationSerializer
from restapi.models import AnnotatedRecording
# Python
import io
import json
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===================================== #
#           Utility Functions           #
# ===================================== #


def get_random_tajweed_rule():
    """Get a random tajweed rule to use along with associated words.
    :return: A tuple with the surah & ayah num, text, rule, and word position
    :rtype: tuple(int, int, str, str, int)
    """
    TAJWEED_FILE = os.path.join(BASE_DIR, 'utils/tajweed.hafs.uthmani-pause-sajdah.json')
    with io.open(TAJWEED_FILE) as file:
        tajweed_rules = json.load(file)
        file.close()

    random_rule = random.choice(tajweed_rules)
    surah_num = random_rule['surah']
    ayah_num = random_rule['ayah']
    annotations = random.choice(random_rule['annotations'])
    rule = annotations['rule']
    rule_start = rule['start']
    rule_end = rule['end']

    del tajweed_rules   # Clean up some memory, maybe not needed...

    UTHMANI_FILE = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(UTHMANI_FILE) as file:
        uthmani_q = json.load(file)
        uthmani_q = uthmani_q['quran']
        file.close()

    # 1-indexed
    ayah_text = uthmani_q['surahs'][surah_num - 1]['ayahs'][ayah_num - 1]['text']
    ayah_text_list = ayah_text.split(" ")
    # Get the index of the word we're looking for
    position = 0
    curr_word_ind = 0
    for i, word in enumerate(ayah_text_list):
        position += len(word)
        if position >= rule_start:
            curr_word_ind = i
            break

    # Make sure we avoid negative count
    prev_word_ind = curr_word_ind - 1 if curr_word_ind > 0 else None
    # Make sure we avoid overflow
    next_word_ind = curr_word_ind + 1 if curr_word_ind + 1 < len(ayah_text_list) else None
    return surah_num, ayah_num, ayah_text, rule, curr_word_ind


# ================================= #
#           API Functions           #
# ================================= #


class TajweedEvaluationList(APIView):
    """API Endpoint that allows tajweed evaluations to be posted or
    retrieved """

    def get(self, request, format=None):
        evaluations = TajweedEvaluation.objects.all().order_by('-timestamp')
        tajweed_serializer = TajweedEvaluationSerializer(evaluations, many=True)
        return Response(tajweed_serializer.data)

    def post(self, request, *args, **kwargs):
        print("EVALUATOR: Received a tajweed evaluation:\n{}".format(request.data))
        # session_id = request.session.session_key or request.data["session_id"]
        # new_evaluation = TajweedEvaluationSerializer(data=request.data)
        # new_evaluation.is_valid(raise_exception=True)
        # new_evaluation.session_id = session_id
        # new_evaluation.save()
        return Response(status=status.HTTP_201_CREATED)

# ===================================== #
#           Static Page Views           #
# ===================================== #


def evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.
    :param request: rest API request object.
    :type request: Request
    :return: Rendered view of evaluator page with ayah and audio url
    :rtype: HttpResponse
    """
    file_name = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        uthmani_quran = json.load(file)
        uthmani_quran = uthmani_quran["quran"]
        file.close()

    files = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
    files = random.sample(list(files), 7)
    file_urls = [f.file.url for f in files if os.path.isfile(f.file.path)]
    ayah_texts = []
    for f in files:
        if os.path.isfile(f.file.path):
            line = uthmani_quran["surahs"][f.surah_num - 1]["ayahs"][f.ayah_num - 1]["text"]
            ayah_texts.append(line)
    file_info = zip(file_urls, ayah_texts)
    return render(request, 'evaluation/evaluator.html', {'file_info': file_info})


def tajweed_evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Rendered view of evaluator page with form, ayah info, and URL.
    :rtype: HttpResponse
    """
    # Get a random recording from the DB
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

    return render(request, 'evaluation/tajweed_evaluator.html',
                  {'degree_category_form': degree_cat_form,
                   'surah_num': surah_num,
                   'ayah_num': ayah_num,
                   'ayah_text': ayah_text.split(" "),
                   'audio_url': audio_url,
                   'recording_id': recording_id})

