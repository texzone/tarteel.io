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
from evaluation.views import TajweedEvaluationList
import restapi.views
from restapi.views import AnnotatedRecordingList, \
    DemographicInformationViewList, RecordingsCount

router = routers.DefaultRouter()
router.register(r'users', restapi.views.UserViewSet)
router.register(r'groups', restapi.views.GroupViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^get_ayah/', audio.views.get_ayah),
    url(r'^get_ayah_translit/', audio.views.get_ayah_translit),
    url(r'^$', audio.views.index),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/recordings/', AnnotatedRecordingList.as_view(),
        name='file-upload'),
    url(r'^api/demographics/', DemographicInformationViewList.as_view(),
        name='demographic'),
    url(r'^get_total_count/', RecordingsCount.as_view(),
        name='recordingscount'),
    url(r'^privacy/', audio.views.privacy),
    url(r'^mobile_app/', audio.views.mobile_app),
    url(r'^about/', audio.views.about),
    url(r'^evaluation/evaluator/', evaluation.views.evaluator),
    url(r'^evaluation/tajweed/', evaluation.views.tajweed_evaluator),
    url(r'^evaluation/submit_tajweed', TajweedEvaluationList.as_view(),
        name='tajweed-evaluation'),
    url(r'^download-audio/', audio.views.download_audio),
    url(r'^sample-recordings/', audio.views.sample_recordings)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
