from django.contrib import admin
from .models import Meeting, Verification, MeetingParticipant, Recording

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("meeting_id", "host", "class_name", "is_active", "created_at")
    search_fields = ("meeting_id", "host__username", "class_name")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("meeting_id", "salt", "created_at")  # Prevent manual editing

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "auth_id", "created_at")
    search_fields = ("user__username", "meeting__meeting_id")
    readonly_fields = ("auth_id", "created_at")

@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "joined_at", "left_at")
    search_fields = ("user__username", "meeting__meeting_id")
    readonly_fields = ("joined_at", "left_at")

@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("meeting", "recorded_by", "file_path", "created_at")
    search_fields = ("meeting__meeting_id", "recorded_by__username")

