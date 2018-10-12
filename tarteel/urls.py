from django.conf.urls import url, include
from rest_framework import routers
import restapi.views

from django.conf.urls import url
from django.contrib import admin
from audio.views import get_ayah, get_ayah_translit, index, privacy, about, mobile_app
from django.conf import settings
from django.conf.urls.static import static

from restapi.views import AnnotatedRecordingList, DemographicInformationViewList, RecordingsCount

router = routers.DefaultRouter()
router.register(r'users', restapi.views.UserViewSet)
router.register(r'groups', restapi.views.GroupViewSet)
# router.register(r'upload-audio', AnnotatedRecordingView.as_view(), base_name="annotated-recording")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^get_ayah/', get_ayah),
    url(r'^get_ayah_translit/', get_ayah_translit),
    url(r'^$', index),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/recordings/', AnnotatedRecordingList.as_view(), name='file-upload'),
    url(r'^api/demographics/', DemographicInformationViewList.as_view(), name='demographic'),
    url(r'^get_total_count/', RecordingsCount.as_view(), name='recordingscount'),
    url(r'^privacy/', privacy),
    url(r'^mobile_app/', mobile_app),
    url(r'^about/', about),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
