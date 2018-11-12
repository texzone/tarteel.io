# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import datetime
import io
import os
import json
import zipfile
from os.path import join, dirname, abspath
from django.db.models import Count
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from restapi.models import AnnotatedRecording, DemographicInformation
from rest_framework.decorators import api_view


# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(abspath(__file__)))

# ===================================== #
#           Utility Functions           #
# ===================================== #


def get_low_ayah_count(quran_dict, line_length):
    """Finds the ayah under the line length with the lowest number of recordings

    :param quran_dict: The uthmani or transliteration quran loaded from a json as a dictionary.
    :type quran_dict: dict
    :param line_length: The maximum number of characters an ayah should have.
    :type line_length: int
    :returns: The surah number, ayah number, and text of the ayah as a tuple.
    :rtype: tuple(int, int, string)
    """
    ayah_counts = list(AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).values(
        'surah_num', 'ayah_num').annotate(count=Count('pk')))
    ayah_count_dict = {(entry['surah_num'], entry['ayah_num']): entry['count'] for entry in ayah_counts}

    min_count = float("inf")
    surah_list = quran_dict['quran']['surahs']
    for surah in surah_list:
        surah_num = int(surah['num'])
        for ayah in surah['ayahs']:
            ayah_num = int(ayah['num'])
            ayah_length = len(ayah['text'])
            if ayah_length < line_length:
                if (surah_num, ayah_num) in ayah_count_dict:  # if it's the shortest ayah, return its information
                    if ayah_count_dict[(surah_num, ayah_num)] <= min_count:
                        ayah_data = surah_num, ayah_num, ayah['text']
                        min_count = ayah_count_dict[(surah_num, ayah_num)]
                else:  # if we have no recordings of this ayah, it automatically takes precedence
                    ayah_data = surah_num, ayah_num, ayah['text']
                    min_count = 0
    return ayah_data


# ================================= #
#           API Functions           #
# ================================= #

@api_view(['GET', 'POST'])
def get_ayah(request, line_length=200):
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

    # Load the Arabic Quran from JSON
    file_name = join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        UTHMANI_QURAN = json.load(file)
        file.close()

    if request.method == 'POST':
        surah = int(request.data['surah'])
        ayah = int(request.data['ayah'])
        # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
        line = UTHMANI_QURAN["quran"]["surahs"][surah - 1]["ayahs"][ayah - 1]["text"]
    else:
        surah, ayah, line = get_low_ayah_count(UTHMANI_QURAN, line_length)

    # Set image file and hash
    image_url = static('img/ayah_images/' + str(surah) + "_" + str(ayah) + '.png')
    req_hash = random.getrandbits(32)

    # Format as json, and save row in DB
    result = {"surah": surah,
              "ayah": ayah,
              "line": line,
              "hash": req_hash,
              "session_id": session_key,
              "image_url": image_url}
    return JsonResponse(result)


@api_view(['POST'])
def get_ayah_translit(request):
    """Returns the transliteration text of an ayah.

    :param request: rest API request object.
    :type request: Request
    :return: A JSON response with the requested text.
    :rtype: JsonResponse
    """
    # Load the Transliteration Quran from JSON
    file_name = join(BASE_DIR, 'utils/data-translit.json')
    with io.open(file_name, 'r', encoding='utf-8-sig') as file:
        TRNSLIT_QURAN = json.load(file)
        file.close()

    surah = int(request.data['surah'])
    ayah = int(request.data['ayah'])

    # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
    line = TRNSLIT_QURAN["quran"]["surahs"][surah - 1]["ayahs"][ayah - 1]["text"]

    # Format as json and return response
    result = {"line": line}

    return JsonResponse(result)


# ===================================== #
#           Static Page Views           #
# ===================================== #
def index(request):
    """index.html page renderer. Gets today's and total recording counts as well as checks
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
    if recording_count > 1000:
        recording_count -= 1000  # because first ~1,000 were test recordings
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    # Check if we need demographics for this session
    ask_for_demographics = DemographicInformation.objects.filter(session_id=session_key).exists()

    daily_count = AnnotatedRecording.objects.filter(
        timestamp__gt=yesterday).exclude(file__isnull=True).count()

    return render(request, 'audio/index.html',
                  {'recording_count': recording_count,
                   'daily_count': daily_count,
                   'ask_for_demographics': ask_for_demographics})


def about(request):
    """about.html page renderer. Includes queries for graphs.

    :param request: rest API request object.
    :type request: Request
    :return: HttpResponse with total number of recordings and labels for graphs
    :rtype: HttpResponse
    """
    # Number of recordings
    recording_count = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).count()

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

    if recording_count > 1000:
        recording_count -= 1000  # because first ~1,000 were test recordings

    return render(request, 'audio/about.html',
                  {'recording_count': recording_count,
                   'gender_labels': gender_labels,
                   'gender_data': gender_data,
                   'age_labels': age_labels,
                   'age_data': age_data,
                   'count_labels': count_labels,
                   'count_data': count_data,
                   'ethnicity_labels': ethnicity_labels,
                   'ethnicity_data': ethnicity_data})


def download_audio(request):
    """download_audio.html renderer.

     :param request: rest API request object.
     :type request: Request
     :return: Just another django mambo.
     :rtype: HttpResponse
     """
    files = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).order_by("?")[:15]
    print([f.file.path for f in files])
    file_urls = [f.file.url for f in files if os.path.isfile(f.file.path)]
    return render(request, 'audio/download_audio.html', {'file_urls': file_urls})


def privacy(request):
    """privacy.html renderer.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    return render(request, 'audio/privacy.html', {})


def mobile_app(request):
    """Special renderer for the mobile browser version of the site.

    :param request: rest API request object.
    :type request: Request
    :return: Response with total number of recordings only.
    :rtype: HttpResponse
    """
    recording_count = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).count()
    if recording_count > 1000:
        recording_count -= 1000
    return render(request, 'audio/mobile_app.html',
                  {"recording_count": recording_count})


def sample_recordings(request):
    """Returns sample media files.

     :param request: rest API request object.
     :type request: Request
     :return: Just another django mambo.
     :rtype: HttpResponse
     """
    files = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).order_by("?")[:50]
    filenames = [f.file.path for f in files if os.path.isfile(f.file.path)]
    zip_subdir = "somefiles"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp
