from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('helpbot/', include('helpbot.urls')),
    path('discussions/', include('discussions.urls')),
    #path("plagiarism-checker/", include("plagiarism_checker.urls")),
    path('plagiarism/', include('plagiarism_checker.urls')),
    path('classroom/', include('classroom.urls')),
    path('calendar/', include('calendarapp.urls')),  
    path('chatroom/', include('chatroom.urls')), 
    path("meetings/", include("meeting_scheduler.urls")),
    path("threeDmodels/", include("threeDmodels.urls")),
    path('whiteboard/',include('whiteboard.urls')),
    path('exam/', include('exam.urls')),
    path('assignments_app/', include('assignments_app.urls')),
    path('flashcards/', include('flashcards.urls')),
    path('conference_meeting/', include('conference_meeting.urls')),   
    path('resource/', include('resource_library.urls')),
]

# Add this for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
