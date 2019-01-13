# Django
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
# REST
from rest_framework import routers
# Tarteel
import audio.views
import evaluation.views
import restapi.views


router = routers.DefaultRouter()
router.register(r'users', restapi.views.UserViewSet)
router.register(r'groups', restapi.views.GroupViewSet)

urlpatterns = [
    # Top Level API
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/recordings/', restapi.views.AnnotatedRecordingList.as_view(),
        name='file-upload'),
    url(r'^api/demographics/', restapi.views.DemographicInformationViewList.as_view(),
        name='demographic'),
    url(r'^api/evaluator/', evaluation.views.EvaluationList.as_view(), name="evaluation"),
    url(r'^api/get_evaluations_count/', evaluation.views.get_evaluations_count,
        name="get_evaluations_count"),
    url(r'^get_ayah/', audio.views.get_ayah),
    url(r'^get_ayah_translit/', audio.views.get_ayah_translit),
    url(r'^get_total_count/', restapi.views.RecordingsCount.as_view(),
        name='recordingscount'),
    url(r'^download-audio/', audio.views.download_audio),
    url(r'^sample-recordings/', audio.views.sample_recordings),
    url(r'^download-full-dataset-csv/', audio.views.download_full_dataset_csv),
    # Audio App (Main Page)
    url(r'^$', audio.views.index),
    url(r'^audio/media/(?:(?P<filename>[-\w]+\.wav)/)?$', audio.views.audio_file),
    url(r'^privacy/', audio.views.privacy),
    url(r'^mobile_app/', audio.views.mobile_app),
    url(r'^about/', audio.views.about),
    url(r'^profile/(?P<session_key>[\w-]+)/', audio.views.profile),
    # Evaluation tools
    url(r'^evaluator/', evaluation.views.evaluator),
    url(r'^evaluation/evaluator/', evaluation.views.evaluator),
    # url(r'^evaluation/help/', evaluation.views.evaluator_help),
    url(r'^evaluation/tajweed/', evaluation.views.tajweed_evaluator),
    url(r'^evaluation/submit_tajweed', evaluation.views.TajweedEvaluationList.as_view(),
        name='tajweed-evaluation'),
    # Django-allauth Login
    url(r'^accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
