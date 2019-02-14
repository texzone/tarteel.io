from django.db import models
from django.forms import ModelForm
from restapi.models import AnnotatedRecording


class TajweedEvaluation(models.Model):
    """A model that contains the information we want to receive from the expert
    regarding the data."""
    # Degree Choices
    MAJOR_DEGREE = 'jali'
    MINOR_DEGREE = 'khafi'
    DEGREE_CHOICES = (
        (MAJOR_DEGREE, 'Jali'),
        (MINOR_DEGREE, 'Khafi')
    )
    # Category Choices
    GHUNNAH = 'ghunnah'
    IDGHAAM_GHUNNAH = 'idghaam_ghunnah'
    IDGHAAM__NO_GHUNNAH = 'idghaam_no_ghunnah'
    IDGHAAM_MUTAJAANISAIN = 'idghaam_mutajaanisain'
    IDGHAAM_MUTAQARIBAIN = 'idghaam_mutaqaribain'
    IDGHAAM_SHAFAWI = 'idghaam_shafawi'
    IKHFA = 'ikhfa'
    IKHFA_SHAFAWI = 'ikhfa_shafawi'
    IQLAB = 'iqlab'
    MADD_2 = 'madd_2'
    MADD_246 = 'madd_246'
    MADD_MUTTASIL = 'madd_muttasil'
    MADD_MUNFASIL = 'madd_munfasil'
    MADD_6 = 'madd_6'
    QALQALAH = 'qalqalah'
    HAMZAT_WASL = 'hamzat_wasl'
    LAM_SHAMSIYYAH = 'lam_shamsiyyah'
    SILENT = 'silent'
    CATEGORY_CHOICES = (
        (GHUNNAH, 'Ghunnah'),
        (IDGHAAM_GHUNNAH, 'Idghaam with Ghunnah'),
        (IDGHAAM__NO_GHUNNAH, 'Idghaam without Ghunnah'),
        (IDGHAAM_MUTAJAANISAIN, 'Idghaam Mutajaanisain'),
        (IDGHAAM_MUTAQARIBAIN, 'Idghaam Mutaqaaribain'),
        (IDGHAAM_SHAFAWI, 'Idghaam Shafawi'),
        (IKHFA, 'Ikhfa'),
        (IKHFA_SHAFAWI, 'Ikhfa Shafawi'),
        (IQLAB, 'Iqlab'),
        (MADD_2, 'Regular Madd'),
        (MADD_246, 'Madd al-Aarid/al-Leen'),
        (MADD_MUTTASIL, 'Madd al-Muttasil'),
        (MADD_MUNFASIL, 'Madd al-Munfasil'),
        (MADD_6, 'Madd Laazim'),
        (QALQALAH, 'Qalqalah'),
        (HAMZAT_WASL, 'Hamzat al-Wasl'),
        (LAM_SHAMSIYYAH, 'Lam al-Shamsiyyah'),
        (SILENT, 'Silent')
    )
    session_id = models.CharField(max_length=32, blank=True)
    platform = models.CharField(max_length=32, default='web')
    # Link the rule evaluation with a specific recording
    associated_recording = models.ForeignKey(AnnotatedRecording,
                                             on_delete=models.CASCADE,
                                             null=True)
    result = models.BooleanField(default=False)
    degree = models.CharField(choices=DEGREE_CHOICES, default=MAJOR_DEGREE,
                              max_length=32)
    category = models.CharField(choices=CATEGORY_CHOICES, default=GHUNNAH,
                                max_length=50)


class TajweedEvaluationForm(ModelForm):
    class Meta:
        model = TajweedEvaluation
        fields = ['degree', 'category']


class Evaluation(models.Model):
    session_id = models.CharField(max_length=32, blank=True)
    associated_recording = models.ForeignKey(AnnotatedRecording,
                                             on_delete=models.CASCADE,
                                             null=True)
    platform = models.CharField(max_length=32, default='web')
    evaluation = models.CharField(max_length=32, default=False)
