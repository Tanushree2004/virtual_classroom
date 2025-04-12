from django.db import models
from django.contrib.auth import get_user_model
from classroom.models import Classroom  # Import Classroom model

User = get_user_model()

class ChatRoom(models.Model):
    classroom = models.OneToOneField(Classroom, on_delete=models.CASCADE, related_name="chatroom")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom for {self.classroom.name}"


class ChatMessage(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ Track edits
    is_deleted = models.BooleanField(default=False)  # ✅ Soft delete

    def __str__(self):
        if self.is_deleted:
            return f"[Deleted] Message from {self.sender.username} in {self.chatroom.classroom.name}"
        return f"Message from {self.sender.username} in {self.chatroom.classroom.name}"
