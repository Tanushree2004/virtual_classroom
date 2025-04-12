from django.urls import path
from .views import lobby, room, meetlist, create_meeting, upload_recording
from django.conf import settings
from django.conf.urls.static import static

app_name = "conference_meeting"

urlpatterns = [
    path('', meetlist, name="meetlist"),
    path('lobby/', lobby, name='lobby'),
    path('lobby/room/', room, name='room'),
    path('create_meeting/',create_meeting, name="create_meeting"),
    path('upload_recording/',upload_recording, name="upload_recording"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

