from django.db import models
from django.conf import settings
from django.utils import timezone
from classroom.models import Classroom


class Assignment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments")
    group = models.CharField(max_length=255, blank=True, null=True)

    """def get_default_classroom():
        return Classroom.objects.get(title="General").id

    group = models.ForeignKey(Classroom, on_delete=models.CASCADE, default=get_default_classroom)"""
    deadline = models.DateTimeField()
    #assignment_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    is_mcq = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
class MCQOptions(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    mcq_answers = models.JSONField(null=True, blank=True)
    descriptive_answers = models.JSONField(null=True, blank=True)
    uploaded_files = models.FileField(upload_to='uploads/',blank=True,null=True)

class Remark(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    text = models.TextField(blank=True,null=True)
    given_at=models.DateTimeField(auto_now=True)

class Notification(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.student.username} at {self.created_at}"