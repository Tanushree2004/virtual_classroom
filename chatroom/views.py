from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from classroom.models import Classroom
from django.views.decorators.csrf import csrf_exempt
import json
@login_required
def get_chatroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if request.user != classroom.instructor and request.user not in classroom.students.all():
        return JsonResponse({"error": "You are not a member of this classroom"}, status=403)
    chatroom, created = ChatRoom.objects.get_or_create(classroom=classroom)
    return JsonResponse({"chatroom_id": chatroom.id})
@login_required
def get_chat_messages(request, chatroom_id):
    chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
    if request.user != chatroom.classroom.instructor and request.user not in chatroom.classroom.students.all():
        return JsonResponse({"error": "You are not a member of this classroom"}, status=403)
    messages = ChatMessage.objects.filter(chatroom=chatroom).order_by('created_at')
    message_list = [
        {
            "id": msg.id,
            "sender": msg.sender.get_full_name() or msg.sender.username,  
            "message": "[Message Deleted]" if msg.is_deleted else msg.message,  
            "attachment": msg.attachment.url if msg.attachment else None,
            "timestamp": msg.created_at.isoformat(),  
            "is_editable": msg.sender == request.user  
        }
        for msg in messages
    ]
    return JsonResponse(message_list, safe=False)
@login_required
def send_chat_message(request, chatroom_id):
    if request.method == "POST":
        chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
        if request.user != chatroom.classroom.instructor and request.user not in chatroom.classroom.students.all():
            return JsonResponse({"error": "You are not a member of this classroom"}, status=403)
        message = request.POST.get("message", "").strip()
        attachment = request.FILES.get("attachment", None)
        if not message and not attachment:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        chat_message = ChatMessage.objects.create(
            chatroom=chatroom,
            sender=request.user,
            message=message,
            attachment=attachment
        )

        return JsonResponse({
            "id": chat_message.id,
            "sender": chat_message.sender.get_full_name() or chat_message.sender.username,
            "message": chat_message.message,
            "attachment": chat_message.attachment.url if chat_message.attachment else None,
            "timestamp": chat_message.created_at.isoformat(),  
            "is_editable": chat_message.sender == request.user 
        })
@login_required
def chatroom_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    chatroom, created = ChatRoom.objects.get_or_create(classroom=classroom)
    return render(request, "chatroom.html", {"chatroom": chatroom, "classroom": classroom})