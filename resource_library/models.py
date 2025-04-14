from django.db import models
from dashboard.models import CustomUser

def resource_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/<folder_name>/<filename>
    folder = instance.category.name if instance.category else "uncategorized"
    return f'{folder}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to=resource_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True) 

    def __str__(self):
        # Display category name or 'Uncategorized' if not set.
        cat = self.category.name if self.category else "Uncategorized"
        return f"{self.title} ({cat})"
