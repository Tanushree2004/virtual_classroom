from django.urls import path
from . import views

app_name = "meeting_scheduler"

urlpatterns = [
    path("all/", views.all_meetings, name="all_meetings"),
    path("create/", views.create_meeting, name="create_meeting"),
    path("meeting/<int:meeting_id>/", views.meeting_detail, name="meeting_detail"),
    path("meeting/<int:meeting_id>/edit/", views.edit_meeting, name="edit_meeting"),
    path("meeting/<int:meeting_id>/delete/", views.delete_meeting, name="delete_meeting"),
    path("meeting/<int:meeting_id>/cancel/", views.cancel_meeting, name="cancel_meeting"),
    path("search/", views.search_meetings, name="search_meetings"),
    path("get_meetings/", views.get_meetings, name="get_meetings"),  # Ensure this is present
    path("update_meeting_status/", views.update_meeting_status, name="update_meeting_status"),
    path("get_meeting_status/", views.get_meeting_status, name="get_meeting_status"), 
]
