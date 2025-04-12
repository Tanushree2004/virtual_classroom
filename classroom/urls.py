from django.urls import path
from . import views

urlpatterns = [
    path('invite/<int:classroom_id>/', views.invite_student, name='invite_student'),
    path('', views.classroom_list, name='classroom_list'),
    path('create/', views.create_classroom, name='create_classroom'),
    path('<int:classroom_id>/edit/', views.edit_classroom, name='edit_classroom'),
    path('<int:classroom_id>/delete/', views.delete_classroom, name='delete_classroom'),
    path('resource/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
    path('<int:classroom_id>/resources/', views.manage_resources, name='manage_resources'),
    path('classroom_resources/<str:filename>/', views.serve_resource, name='serve_resource'),
]
