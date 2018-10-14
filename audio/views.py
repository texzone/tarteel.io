# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import datetime
import io
import json
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from restapi.models import AnnotatedRecording, DemographicInformation
from rest_framework.decorators import api_view
from .data import COUNTRIES
import sqlite3

END_OF_FILE = 6236


class AyahDistFinder:
    """Reads an SQL DB table, counts how many """
    def __init__(self):

        self.DB_FILENAME = '../db.sqlite3'
        self.DB = sqlite3.connect(self.DB_FILENAME)
        self.AYAH_COUNTS_BY_SURAH = [{} for i in range(114)]  # Surah Num: List of Ayahs and counts
        self.SQL_TABLE_READ = False
        self.lowest_count_surah_num = 0
        self.lowest_count_ayah_num = 0

    def read_sql_ayahs(self):
        # Indices for SQL Table
        SURAH_NUM = 2
        AYAH_NUM = 3
        # Setup dict to store info
        cursor = self.DB.cursor()
        cursor.execute('''SELECT * FROM restapi_annotatedrecording''')
        table = cursor.fetchall()
        for row in table:
            # Get the dict of ayah counts
            ayah_counts = self.AYAH_COUNTS_BY_SURAH[row[SURAH_NUM] - 1]
            # See if a count record exists
            count = ayah_counts.get(row[AYAH_NUM])
            # Increment if it exists, create otherwise and make this the new low
            if count:
                count += 1
                ayah_counts[row[AYAH_NUM]] = count
            else:
                ayah_counts[row[AYAH_NUM]] = 1
                self.lowest_count_surah_num = row[SURAH_NUM]
                self.lowest_count_ayah_num = row[AYAH_NUM]
        self.SQL_TABLE_READ = True

    def get_low_surah_ayah(self):
        if not self.SQL_TABLE_READ:
            self.read_sql_ayahs()
        return self.lowest_count_surah_num, self.lowest_count_ayah_num


ayah_finder = AyahDistFinder()


# get_ayah gets the surah num, ayah num, and text of a random ayah of a specified maximum length
@api_view(['GET', 'POST'])
def get_ayah(request, line_length=200):
    # user tracking - ensure there is always a session key
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Get line
    with io.open('data-uthmani.json', 'r', encoding='utf-8-sig') as f:
        lines = json.load(f)
        f.close()

    if request.method == 'POST':
        surah = int(request.data['surah'])
        ayah = int(request.data['ayah'])
    else:
        surah, ayah = ayah_finder.get_low_surah_ayah()

    # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
    line = lines["quran"]["surahs"][surah - 1]["ayahs"][ayah - 1]["text"]
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


@api_view(['GET', 'POST'])
def get_ayah_translit(request, line_length=200):
    """
    Returns the transliteration of an ayah
    """
    # user tracking - ensure there is always a session key
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Read Transliteration file
    with io.open('../utils/data-translit.json', 'r', encoding='utf-8') as f:
        lines = json.load(f)
        f.close()

    if request.method == 'POST':
        surah = int(request.data['surah'])
        ayah = int(request.data['ayah'])
    else:
        surah = random.randint(1, 114)
        ayah = random.randint(1, len(lines["quran"][surah]["ayahs"]))

    # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
    line = lines["quran"][surah - 1]["ayahs"][ayah - 1]["text"]
    req_hash = random.getrandbits(32)

    # Format as json, and save row in DB
    result = {"surah": surah,
              "ayah": ayah,
              "line": line,
              "hash": req_hash,
              "session_id": session_key}

    return JsonResponse(result)


#########################
#                       #
# Static Page Views     #
#                       #
#########################


def index(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    recording_count = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False).count()
    if recording_count > 1000:
        recording_count -= 1000  # because roughly our first 1,000 were test recordings
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    if DemographicInformation.objects.filter(session_id=session_key).exists():
        ask_for_demographics = False
    else:
        ask_for_demographics = True

    daily_count = AnnotatedRecording.objects.filter(
        timestamp__gt=yesterday).exclude(file__isnull=True).count()

    return render(request, 'audio/index.html',
                  {'recording_count': recording_count,
                   'daily_count': daily_count,
                   'ask_for_demographics': ask_for_demographics,
                   'countries': COUNTRIES})


def about(request):
    recording_count = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False).count()
    if recording_count > 1000:
        recording_count -= 1000  # because roughly our first 1,000 were test recordings
    return render(request, 'audio/about.html', {'recording_count': recording_count})


def privacy(request):
    return render(request, 'audio/privacy.html', {})


def mobile_app(request):
    recording_count = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False).count()
    if recording_count > 1000:
        recording_count -= 1000
    return render(request, 'audio/mobile_app.html', {"recording_count": recording_count})
