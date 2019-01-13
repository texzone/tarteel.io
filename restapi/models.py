from __future__ import unicode_literals

# Create your models here.
from django.db import models


class DemographicInformation(models.Model):
    session_id = models.CharField(max_length=32, blank=True)
    # This could be used to store different platforms such as android,
    # ios, web if different identification methods are used for each one.
    platform = models.CharField(max_length=256, default='web')
    gender = models.CharField(max_length=32)
    qiraah = models.CharField(max_length=32, blank=True, null=True)
    age = models.CharField(max_length=32)
    ethnicity = models.CharField(max_length=32, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class AnnotatedRecording(models.Model):
    file = models.FileField(blank=True, null=True)
    surah_num = models.IntegerField(blank=True, null=True)
    ayah_num = models.IntegerField(blank=True, null=True)
    hash_string = models.CharField(max_length=32)
    recitation_mode = models.CharField(max_length=32, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # TODO(implement timeout)
    session_id = models.CharField(max_length=32)
    is_evaluated = models.BooleanField(default=False)
    associated_demographic = models.ForeignKey(DemographicInformation,
                                               on_delete=models.SET_NULL,
                                               null=True, blank=True, default=None)
