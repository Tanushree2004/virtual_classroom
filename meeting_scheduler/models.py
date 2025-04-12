from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_meetings")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="meetings")
    scheduled_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Upcoming")

    def update_status(self):
        """Update meeting status dynamically based on current time."""
        current_time = now()  # Already timezone-aware

        if self.status == "Canceled":
            return  # Don't update canceled meetings

        if not self.end_time:  
            return  # If no end_time, do nothing to avoid errors

        # Determine new status
        if self.scheduled_time <= current_time < self.end_time:
            new_status = "Ongoing"
        elif current_time >= self.end_time:
            new_status = "Completed"
        else:
            new_status = "Upcoming"

        # Update only if status has changed
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])
