from django.urls import path
from . import views

app_name = "chatroom"

urlpatterns = [
    path('<int:classroom_id>/', views.chatroom_view, name='chatroom_view'),
    path('<int:classroom_id>/chatroom/', views.get_chatroom, name='get_chatroom'),
    path('<int:chatroom_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('<int:chatroom_id>/send/', views.send_chat_message, name='send_chat_message'),
]
