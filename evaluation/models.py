from django.db import models
from django.forms import ModelForm


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
    recording_id = models.CharField(max_length=32, blank=False)
    platform = models.CharField(max_length=32, default='web')
    letter = models.CharField(max_length=1)
    # Letter position in the Ayah
    letter_position = models.IntegerField(default=0)
    degree = models.CharField(choices=DEGREE_CHOICES, default=MAJOR_DEGREE,
                              max_length=32)
    category = models.CharField(choices=CATEGORY_CHOICES, default=PROLONGATION,
                                max_length=32)


class TajweedEvaluationForm(ModelForm):
    class Meta:
        model = TajweedEvaluation
        fields = ['degree', 'category']
