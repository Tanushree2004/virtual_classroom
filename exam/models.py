from django.db import models
from django.conf import settings
from django.utils import timezone

class Exam(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exams")
    group = models.CharField(max_length=255, blank=True, null=True)
    deadline = models.DateField(null=True)
    start_duration = models.TimeField(null=True)
    end_duration = models.TimeField(null=True)

    seen_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='seen_exams')
    
    def __str__(self):
        return self.name
    
class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="examquestions")
    text = models.TextField()
    is_mcq = models.BooleanField(default=False)
    question_attachment = models.FileField(upload_to='exam_question_attachments/', null=True, blank=True)
    marks = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.text
    
class ExamMCQOptions(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name="examoptions")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="examsubmissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    mcq_answers = models.JSONField(null=True, blank=True)
    descriptive_answers = models.JSONField(null=True, blank=True)
    uploaded_files = models.FileField(upload_to='uploads/',blank=True,null=True)

"""class Remark(models.Model):
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
"""