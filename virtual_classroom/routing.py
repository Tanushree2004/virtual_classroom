from django.urls import path
from chatroom.routing import websocket_urlpatterns as app1_websockets
from conference_meeting.routing import websocket_urlpatterns as app2_websockets

websocket_urlpatterns = app1_websockets + app2_websockets
