from django.urls import path
from .consumers import MeetingConsumer

websocket_urlpatterns = [
    path("ws/conference_meeting/<str:room_name>/", MeetingConsumer.as_asgi()),
]