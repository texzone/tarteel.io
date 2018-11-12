from django.shortcuts import render
import json
import io
import os
from os.path import join, dirname, abspath
from django.shortcuts import render
from restapi.models import AnnotatedRecording


# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(abspath(__file__)))


# Create your views here.
def evaluator(request):
    """privacy.html renderer.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    file_name = join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        uthmani_quran = json.load(file)
        file.close()

    files = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).order_by("?")[:7]
    file_urls = [f.file.url for f in files if os.path.isfile(f.file.path)]
    ayah_texts = []
    for f in files:
        if os.path.isfile(f.file.path):
            line = uthmani_quran["quran"]["surahs"][f.surah_num - 1]["ayahs"][f.ayah_num - 1]["text"]
            ayah_texts.append(line)
    file_info = zip(file_urls, ayah_texts)
    return render(request, 'evaluation/evaluator.html', {'file_info': file_info})
