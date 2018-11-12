# Django
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms import modelformset_factory
from django.shortcuts import render
from evaluation.models import TajweedEvaluation
from restapi.models import AnnotatedRecording

# RestAPI
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Python
from random import choice


def evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    # Get a random recording from the DB (Please don't use order_by('?')[0] :) )
    recording_ids = list(AnnotatedRecording.objects.values_list('id', flat=True))
    random_id = choice(recording_ids)
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

    return render(request, 'evaluation/evaluator.html',
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