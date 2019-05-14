from django.urls import path, include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register('recordings', views.AnnotatedRecordingViewSet)
router.register('evaluations', views.EvaluationViewSet)

urlpatterns = [ path('', include(router.urls)) ]
