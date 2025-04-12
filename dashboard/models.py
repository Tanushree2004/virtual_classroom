from django.contrib.auth.models import AbstractUser
from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    database_name = models.CharField(max_length=255, unique=True)  # DB name for the institution

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Instructor', 'Instructor'),
        ('Student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    # Fields for students
    session_year = models.CharField(max_length=10, blank=True, null=True)
    semester = models.CharField(max_length=10, blank=True, null=True)
    student_class = models.CharField(max_length=100, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)

    # Fields for instructors & admins
    faculty = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    profile_image = models.ImageField(upload_to="profile_images/", default="default.jpg")

    def __str__(self):
        return self.username
class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ]
    FONT_SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    FONT_STYLE_CHOICES = [
    ('sans-serif', 'Sans Serif'),
    ('serif', 'Serif'),
    ('monospace', 'Monospace'),
    ('inter', 'Inter'),
    ('poppins', 'Poppins'),
    ('roboto', 'Roboto'),
]

    

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    font_size = models.CharField(max_length=10, choices=FONT_SIZE_CHOICES, default='medium')
    font_style = models.CharField(max_length=20, choices=FONT_STYLE_CHOICES, default='sans-serif')

    def __str__(self):
        return f"{self.user.username}'s Preferences"