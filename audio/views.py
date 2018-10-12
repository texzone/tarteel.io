# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import datetime
import io
import json
from django.db.models import Count
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from restapi.models import AnnotatedRecording, DemographicInformation
from rest_framework.decorators import api_view
from collections import Counter

END_OF_FILE = 6236

# get_ayah gets the surah num, ayah num, and text of a random ayah of
# a specified maximum length
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
        surah = random.randint(1, 114)
        ayah = random.randint(1, len(lines["quran"]["surahs"][surah]["ayahs"]))

    # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
    line = lines["quran"]["surahs"][surah-1]["ayahs"][ayah-1]["text"]
    image_url = static('img/ayah_images/'+str(surah)+"_"+str(ayah)+'.png')
    hash = random.getrandbits(32)

    # Format as json, and save row in DB
    result = {"surah": surah, "ayah": ayah, "line": line, "hash": hash,
              "session_id": session_key, "image_url": image_url}

    return JsonResponse(result)

################################################################################
############################## static page views ###############################
################################################################################
def index(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    recording_count = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).count()
    if recording_count > 1000:
       recording_count -= 1000  # because first ~1,000 were test recordings
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
         'ask_for_demographics':ask_for_demographics})

def about(request):
    recording_count = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).count()

    ### Get demographic data for the graphs.
    gender_labels = ['male', 'female']
    gender_counts = DemographicInformation.objects.filter(
        gender__in=gender_labels).values('gender').annotate(
            the_count=Count('gender'))
    gender_labels  = [k['gender'] for k in gender_counts]
    gender_data = [k['the_count'] for k in gender_counts]

    age_labels = ['13', '19', '26', '36', '46', '56']
    age_counts = DemographicInformation.objects.filter(
        age__in=age_labels).values('age').annotate(
            the_count=Count('age'))
    age_labels  = [k['age'] for k in age_counts]
    age_label_map = {'13':'13-18',
                     '19':'19-25',
                     '26':'26-35',
                     '36':'36-45',
                     '46':'46-55',
                     '56':'56+'}
    age_labels = [age_label_map[a] for a in age_labels]
    age_data = [k['the_count'] for k in age_counts]

    ethnicity_counts = DemographicInformation.objects.values(
        'ethnicity').annotate(the_count=Count('ethnicity')).order_by(
            '-the_count')[:6]
    ethnicity_labels  = [k['ethnicity'] for k in ethnicity_counts]
    ethnicity_data = [k['the_count'] for k in ethnicity_counts]

    ### Get ayah data for the graphs.
    ayah_counts = list(AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).values(
        'surah_num', 'ayah_num').annotate(count=Count('pk')))
    raw_counts = [ayah['count'] for ayah in ayah_counts]
    count_labels = ['0', '1', '2', '3', '4', '5+']
    count_data = [
        END_OF_FILE - len(ayah_counts),  # ayahs not in list have 0 count
        raw_counts.count(1),
        raw_counts.count(2),
        raw_counts.count(3),
        raw_counts.count(4)]
    count_data.append(END_OF_FILE - sum(count_data)) # remaining have 5+ count


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

def privacy(request):
    return render(request, 'audio/privacy.html', {})

def mobile_app(request):
    recording_count = AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).count()
    if recording_count > 1000:
        recording_count -= 1000
    return render(request, 'audio/mobile_app.html',
                  {"recording_count": recording_count})
