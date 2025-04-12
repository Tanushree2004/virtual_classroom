from django.urls import path
from .views import calendar_view, get_meetings,update_meeting_date

urlpatterns = [
    path('', calendar_view, name='calendar_view'),
    path('events/', get_meetings, name='get_meetings'),
    path('update-meeting-date/', update_meeting_date, name='update_meeting_date'),  # ✅ Fix added

]

