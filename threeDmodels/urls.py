from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path

app_name="threeDmodels"

urlpatterns = [
     path('delete-model/<int:model_id>/', views.delete_model, name='delete_model'),
     path('upload/', views.upload_3d_model, name='upload_3d_model'),
     path("models/", views.model_list, name="model_list"),
     
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
