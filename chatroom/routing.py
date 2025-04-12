from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chatroom/<int:classroom_id>/", ChatConsumer.as_asgi()),
]
