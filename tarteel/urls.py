from django.conf.urls import url, include
from rest_framework import routers
import restapi.views

from django.conf.urls import url
from django.contrib import admin
import audio.views
import evaluation.views
from django.conf import settings
from django.conf.urls.static import static

from restapi.views import AnnotatedRecordingList, DemographicInformationViewList, RecordingsCount
from evaluation.views import EvaluationList, get_evaluations_count

router = routers.DefaultRouter()
router.register(r'users', restapi.views.UserViewSet)
router.register(r'groups', restapi.views.GroupViewSet)
# router.register(r'upload-audio', AnnotatedRecordingView.as_view(), base_name="annotated-recording")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^get_ayah/', audio.views.get_ayah),
    url(r'^get_ayah_translit/', audio.views.get_ayah_translit),
    url(r'^$', audio.views.index),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/recordings/', AnnotatedRecordingList.as_view(), name='file-upload'),
    url(r'^api/demographics/', DemographicInformationViewList.as_view(), name='demographic'),
    url(r'^get_total_count/', RecordingsCount.as_view(), name='recordingscount'),
    url(r'^privacy/', audio.views.privacy),
    url(r'^mobile_app/', audio.views.mobile_app),
    url(r'^about/', audio.views.about),
    url(r'^profile/(?P<session_key>[\w-]+)/', audio.views.profile),
    url(r'^evaluator/', evaluation.views.evaluator),
    url(r'^api/evaluator/', EvaluationList.as_view(), name="evaluation"),
    url(r'^api/get_evaluations_count/', evaluation.views.get_evaluations_count, name="get_evaluations_count"),
    url(r'^download-audio/', audio.views.download_audio),
    url(r'^sample-recordings/', audio.views.sample_recordings),
    url(r'^download-full-dataset-csv/', audio.views.download_full_dataset_csv)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
