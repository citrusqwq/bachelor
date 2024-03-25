from django.urls import re_path

from ViViPlayer.urls import MEETING_PATH
from websocket import consumer

websocket_urlpatterns = [
    re_path(r'ws/' + MEETING_PATH + r'(?P<meetingName>\w+)/$',
            consumer.MeetingConsumer.as_asgi()),
]
