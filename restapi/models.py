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
