import uuid
from django.db import models
from django.conf import settings
from .utils import generate_meeting_id, generate_hmac_id
from django.utils.crypto import get_random_string
import hashlib


# 1️⃣ Meeting Model (Stores Meeting Details & Security Info)
class Meeting(models.Model):
    meeting_id = models.CharField(max_length=64, unique=True, primary_key=True)  # Hashed ID (X)
    salt = models.CharField(max_length=64, unique=True)  # Random salt (S)
    secret_key = models.CharField(max_length=256)  # Encrypted ABC key
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Instructor/Admin who created the meeting
    class_name = models.CharField(max_length=255)  # Associated class
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of meeting creation
    is_active = models.BooleanField(default=False)  # Meeting status

    def save(self, *args, **kwargs):
        if not self.meeting_id:
            self.meeting_id = generate_meeting_id(self.meeting_name,self.class_name, self.host.username)
        if not self.salt:
            self.salt = uuid.uuid4().hex  # Generates a secure salt
        if not self.secret_key:
            self.secret_key =  hashlib.sha256(get_random_string(32).encode()).hexdigest()
        super().save(*args, **kwargs)

    def get_secure_meeting_link(self):
        return generate_hmac_id(self.meeting_id, self.salt, self.secret_key)

# 2️⃣ Verification Model (For User Authentication)
class Verification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The participant (student/instructor)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)  # Linked meeting
    auth_id = models.CharField(max_length=64, unique=True)  # HMAC(Username + Role)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when Z was generated

# 3️⃣ Meeting Participants Model (Tracks Who Joins/Leaves)
class MeetingParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The participant
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)  # Linked meeting
    joined_at = models.DateTimeField(auto_now_add=True)  # Time user joined
    left_at = models.DateTimeField(null=True, blank=True)  # Time user left

# 4️⃣ Recording Model (Stores Meeting Recordings)
class Recording(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)  # Linked meeting
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who recorded the meeting
    file_path = models.CharField(max_length=500)  # Path to stored recording
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of recording
