# helpbot/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('', views.helpbot_home, name='helpbot_home'),
    path('ask/', views.get_help_response, name='helpbot_ask'),

]
