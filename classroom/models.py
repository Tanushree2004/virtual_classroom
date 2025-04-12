from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Classroom(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Instructor'})
    students = models.ManyToManyField(User, related_name='classrooms', limit_choices_to={'role': 'Student'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ClassroomResource(models.Model):
    RESOURCE_TYPES = [
        ('file', 'File'),
        ('link', 'Link'),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='classroom_resources/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

