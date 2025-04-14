from django.urls import path
from . import views

app_name = "resource_library"

urlpatterns = [
    path('', views.home, name='home'),
    path('delete-folder/<int:category_id>/', views.delete_folder, name='delete_folder'),
    path('add-folder/', views.add_folder, name='add_folder'),
    path('upload/', views.resource_upload, name='resource_upload'),
    path('category/<str:category_name>/', views.resource_list, name='resource_list'),
    path('download/<int:resource_id>/', views.resource_download, name='resource_download'),
    path('delete/<int:resource_id>/', views.resource_delete, name='resource_delete'),
]
