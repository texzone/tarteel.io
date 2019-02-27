# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict
import csv
import datetime
import io
import json
import os
import random
import requests
import zipfile
from os.path import join, dirname, abspath
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.timezone import utc
from restapi.models import AnnotatedRecording, DemographicInformation
from rest_framework.decorators import api_view
from ranged_fileresponse import RangedFileResponse


# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(abspath(__file__)))
INT_NA_VALUE = -1
STRING_NA_VALUE = "N/A"

# ===================================== #
#           Utility Functions           #
# ===================================== #


def get_low_ayah_count(quran_dict, line_length):
    """Finds the ayah under the line length with the lowest number of recordings

    :param quran_dict: The uthmani or transliteration quran loaded from a json
    as a dictionary.
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
    ayah_data_list = []
    for surah in surah_list:
        surah_num = int(surah['num'])
        for ayah in surah['ayahs']:
            ayah_num = int(ayah['num'])
            ayah_length = len(ayah['text'])
            if ayah_length < line_length:
                if (surah_num, ayah_num) in ayah_count_dict:  # if it's the shortest ayah, return its information
                    if ayah_count_dict[(surah_num, ayah_num)] < min_count:
                        ayah_data = surah_num, ayah_num, ayah['text']
                        ayah_data_list = [ayah_data]
                        min_count = ayah_count_dict[(surah_num, ayah_num)]
                    elif ayah_count_dict[(surah_num, ayah_num)] == min_count:
                        ayah_data = surah_num, ayah_num, ayah['text']
                        ayah_data_list.append(ayah_data)
                else:  # if we have no recordings of this ayah, it automatically takes precedence
                    ayah_data = surah_num, ayah_num, ayah['text']
                    if min_count == 0:
                        ayah_data_list.append(ayah_data)
                    else:
                        ayah_data_list.append(ayah_data)
                        min_count = 0
    return random.choice(ayah_data_list)


def _sort_recitations_dict_into_lists(dictionary):
    """ Helper method that simply converts a dictionary into two lists sorted
    correctly.

    :param dictionary: Dict of two lists
    :type dictionary: dict
    :return Sorted dict
    :rtype dict
    """
    if not dictionary:
        return zip([], [])
    surah_nums, ayah_lists = zip(*dictionary.items())
    surah_nums, ayah_lists = list(surah_nums), list(ayah_lists)
    surah_nums, ayah_tuples = zip(*sorted(
        zip(surah_nums, ayah_lists)))  # Now they are sorted according to surah_nums
    for i in range(len(ayah_lists)):
        ayah_lists[i] = sorted(list(ayah_tuples[i]))
    return zip(surah_nums, ayah_lists)


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
    req_hash = random.getrandbits(32)

    # Format as json, and save row in DB
    result = {"surah": surah,
              "ayah": ayah,
              "line": line,
              "hash": req_hash,
              "session_id": session_key}
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

def stream_audio_url(request, url):
    file = requests.get(url, allow_redirects=True)
    response = RangedFileResponse(request, file.content, content_type='audio/wav')
    response['Content-Disposition'] = 'attachment; filename="evaluation.wav"'
    return response


def about(request):
    """about.html page renderer. Includes queries for graphs.

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
    # Add commas to this number as it is used for display.
    recording_count_formatted = "{:,}".format(recording_count)

    return render(request, 'audio/about.html',
                  {'recording_count': recording_count,
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
                   'ethnicity_data': ethnicity_data})


def profile(request, session_key):
    """download_audio.html renderer.

     :param request: rest API request object.
     :type request: Request
     :param session_key: string representing the session key for the user
     :type session_key: str
     :return: Just another django mambo.
     :rtype: HttpResponse
     """
    # This may be different from the one provided in the URL.
    my_session_key = request.session.session_key
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

    return render(request, 'audio/profile.html', {'session_key': my_session_key,
                                                  'recent_dict': dict(recent_dict),
                                                  'recent_lists': recent_lists,
                                                  'old_lists': old_lists,
                                                  'dates': dates[::-1],
                                                  'weekly_counts': weekly_counts[::-1],
                                                  'old_dict': dict(old_dict),
                                                  'recording_count': recording_count,
                                                  'user_recording_count': user_recording_count})


def download_audio(request):
    """download_audio.html renderer. Returns the URLs of 15 random, non-empty
    audio samples.

     :param request: rest API request object.
     :type request: Request
     :return: Response with list of file urls.
     :rtype: HttpResponse
     """
    files = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False).order_by('timestamp')[5000:6000]
    random.seed(0)  # ensures consistency in the files displayed.
    rand_files = random.sample(list(files), 15)
    file_urls = [f.file.url for f in rand_files]
    return render(request, 'audio/download_audio.html', {'file_urls': file_urls})


def download_full_dataset_csv(request):
    """Returns a csv with a URL and metadata for all recordings.

     :param request: rest API request object.
     :type request: Request
     :return: Just another django mambo.
     :rtype: HttpResponse
     """

    files = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).order_by('?')[:25000]
    download_timestamp = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d-%H:%M")
    csv_filename = "tarteel-io_full_dataset_%s.csv" % download_timestamp

    # Create the HttpResponse object with the appropriate CSV header.
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=%s' % csv_filename

    # Create the CSV file and fill its headings.
    writer = csv.writer(resp)
    writer.writerow(['Surah Number',
                     'Ayah Number',
                     'URL to Recording',
                     'Age',
                     'Country',
                     'Gender',
                     'Qiraah',
                     'Recitation Mode',
                     'Timestamp of Recording Submission',
                     'Has This Recording Been Evaluated?'])

    # Fill the CSV file; if the desired demographic info does not exist, use placeholders to denote N/A.
    for f in files:
        # TODO(hamz) At some point, we need to properly link demographic info to recordings in the model.
        demographic_info_list = DemographicInformation.objects.filter(session_id=f.session_id).order_by('-timestamp')

        if demographic_info_list.exists():
            # Get the most recently updated demographics info.
            demographic_info = demographic_info_list[0]
            age = demographic_info.age
            ethnicity = demographic_info.ethnicity
            gender = demographic_info.gender
            qiraah = demographic_info.qiraah
        else:
            # If no demographic info associated, then fill the fields with defaults.
            age = INT_NA_VALUE
            ethnicity = STRING_NA_VALUE
            gender = STRING_NA_VALUE
            qiraah = STRING_NA_VALUE

        writer.writerow([f.surah_num,
                         f.ayah_num,
                         f.file.url,
                         age,
                         ethnicity,
                         gender,
                         qiraah,
                         f.recitation_mode,
                         f.timestamp,
                         f.is_evaluated])

    return resp


# TODO(abidlabs): file.path is no longer supported once the recordings were moved to AWS.
def sample_recordings(request):
    """Returns 50 sample media files in ZIP format

     :param request: rest API request object.
     :type request: Request
     :return: A response with a ZIP file containing audio samples.
     :rtype: HttpResponse
     """
    files = AnnotatedRecording.objects.filter(file__isnull=False)
    rand_files = random.sample(list(files), 50)
    filenames = [f.file.path for f in rand_files if os.path.isfile(f.file.path)]
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
