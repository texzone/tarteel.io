# -*- coding: utf-8 -*-
# Django
from django.forms import modelformset_factory
from django.shortcuts import render
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

# ================================= #
#           API Functions           #
# ================================= #


# class TajweedEvaluationList(APIView):
#     def post(self, request, *args, **kwargs):
#         session_id = request.session.session_key or request.data["session_id"]
#         new_evaluation = TajweedEvaluationSerializer(data=request.data)
#         new_evaluation.is_valid(raise_exception=True)
#         new_evaluation.session_id = session_id
#         new_evaluation.save()
#         return Response(status=status.HTTP_201_CREATED)


# ===================================== #
#           Static Page Views           #
# ===================================== #


def evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.
    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    file_name = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        uthmani_quran = json.load(file)
        file.close()

    files = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
    files = random.sample(list(files), 7)
    file_urls = [f.file.url for f in files if os.path.isfile(f.file.path)]
    ayah_texts = []
    for f in files:
        if os.path.isfile(f.file.path):
            line = uthmani_quran["quran"]["surahs"][f.surah_num - 1]["ayahs"][f.ayah_num - 1]["text"]
            ayah_texts.append(line)
    file_info = zip(file_urls, ayah_texts)
    return render(request, 'evaluation/evaluator.html', {'file_info': file_info})


def tajweed_evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    file_name = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        uthmani_quran = json.load(file)
        file.close()

    files = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False)
    files = random.sample(list(files), 7)
    file_urls = [f.file.url for f in files if os.path.isfile(f.file.path)]
    ayah_texts = []
    for f in files:
        if os.path.isfile(f.file.path):
            line = uthmani_quran["quran"]["surahs"][f.surah_num - 1]["ayahs"][f.ayah_num - 1]["text"]
            ayah_texts.append(line)
    file_info = zip(file_urls, ayah_texts)
    return render(request, 'evaluation/evaluator.html', {'file_info': file_info})


def tajweed_evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
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

    return render(request, 'evaluation/tajweed_evaluator.html',
                  {'degree_category_form': degree_cat_form,
                   'surah_num': surah_num,
                   'ayah_num': ayah_num,
                   'ayah_text': ayah_text.split(" "),
                   'audio_url': audio_url,
                   'recording_id': recording_id})


class TajweedEvaluationList(APIView):
    """API Endpoint that allows tajweed evaluations to be posted or
    retrieved """

    def get(self, request, format=None):
        evaluations = TajweedEvaluation.objects.all().order_by('-timestamp')
        tajweed_serializer = TajweedEvaluationSerializer(evaluations, many=True)
        return Response(tajweed_serializer.data)

    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key or request.data["session_id"]
        print(request.data)
        # new_eval = TajweedEvaluationSerializer(data=request.data)
        # try:
        #     new_eval.is_valid(raise_exception=True)
        #     new_eval.save()
        return Response(status=status.HTTP_201_CREATED)
        # except serializers.ValidationError:
        #     return Response(new_eval.errors, status=status.HTTP_400_BAD_REQUEST)

