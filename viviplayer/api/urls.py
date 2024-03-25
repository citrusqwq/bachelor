from django.urls import path, include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r'meeting', views.MeetingApiViewSet, basename='Meeting Api ViewSet')

urlpatterns = [
    path('', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]