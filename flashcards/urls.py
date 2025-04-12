from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'flashcards'
urlpatterns = [
    path('upload/',views.upload_file, name='upload_file'),
    path('test-base-dir/', views.test_base_dir, name='test_base_dir'),
    path('check-file/', views.check_file_path, name='check_file_path'),
    path('process-flashcards/', views.process_flashcards, name='process_flashcards'),
    path('show-flashcards/<int:file_id>/', views.show_flashcards, name='show_flashcards'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)