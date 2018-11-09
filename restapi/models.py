from __future__ import unicode_literals

# Create your models here.
from django.db import models


class AnnotatedRecording(models.Model):
    file = models.FileField(blank=True, null=True)
    surah_num = models.IntegerField(blank=True, null=True)
    ayah_num = models.IntegerField(blank=True, null=True)
    hash_string = models.CharField(max_length=32)
    recitation_mode = models.CharField(max_length=32, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # TODO(implement timeout)
    session_id = models.CharField(max_length=32)


class DemographicInformation(models.Model):
    session_id = models.CharField(max_length=32, blank=True)
    # This could be used to store different platforms such as android,
    # ios, web if different identificaiton methods are used for each one.
    platform = models.CharField(max_length=32, default='web')
    gender = models.CharField(max_length=32)
    qiraah = models.CharField(max_length=32, blank=True, null=True)
    age = models.CharField(max_length=32)
    ethnicity = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=32, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class TajweedInformation(models.Model):
    # Degree Choices
    MAJOR_DEGREE = 'jali'
    MINOR_DEGREE = 'khafi'
    DEGREE_CHOICES = (
        (MAJOR_DEGREE, 'Jali'),
        (MINOR_DEGREE, 'Khafi')
    )
    # Category Choices
    PROLONGATION = 'madd'
    FATTENING = 'tafkheem'
    THINNING = 'tarqeeq'
    EMISSION = 'makharij'
    # Theres sakinah and mushaddadah
    NOON = 'noon'
    MEEM = 'meem'
    ECHO = 'qalqala'
    OTHER = 'other'
    CATEGORY_CHOICES = (
        (PROLONGATION, 'Prolongation'),
        (FATTENING, 'Fattening'),
        (THINNING, 'Thinning'),
        (EMISSION, 'Emission'),
        (NOON, 'Noon'),
        (MEEM, 'Meem'),
        (ECHO, 'Echo'),
        (OTHER, 'Other'),
    )
    session_id = models.CharField(max_length=32, blank=True)
    recording_id = models.CharField(max_length=32)
    platform = models.CharField(max_length=32, default='web')
    letter = models.CharField(max_length=1)
    # Letter position in the Ayah
    letter_position = models.IntegerField(default=0)
    degree = models.CharField(choices=DEGREE_CHOICES, default=MAJOR_DEGREE, max_length=32)
    category = models.CharField(choices=CATEGORY_CHOICES, default=PROLONGATION, max_length=32)
