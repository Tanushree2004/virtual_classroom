from django.urls import path
from .views import plagiarism_checker_view

urlpatterns = [
    path('check/', plagiarism_checker_view, name='plagiarism_checker'),
]
