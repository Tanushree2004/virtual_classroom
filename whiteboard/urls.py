from django.urls import path
from .views import dashboard, create_whiteboard, edit_whiteboard, save_whiteboard, delete_whiteboard
from django.conf import settings
from django.conf.urls.static import static

app_name = 'whiteboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('create/', create_whiteboard, name='create_whiteboard'),
    path('edit/<int:board_id>/', edit_whiteboard, name='edit_whiteboard'),
    path('save/<int:board_id>/', save_whiteboard, name='save_whiteboard'),
    path('delete/<int:board_id>/', delete_whiteboard, name='delete_whiteboard'),  # New delete route
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
