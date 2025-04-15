# helpbot/urls.py
from django.urls import path
from . import views

app_name = "helpbot"  # This registers the namespace

urlpatterns = [
    path('', views.helpbot_home, name='helpbot_home'),
    path('ask/', views.get_help_response, name='helpbot_ask'),
    path('update-name/', views.update_helpbot_name, name='update_helpbot_name'),
]
