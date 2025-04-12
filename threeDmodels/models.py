from django.db import models
import os

def model_upload_path(instance, filename):
    """Store 3D models in a separate folder inside `classroom_resources/`."""
    return os.path.join("3dmodels/", filename)  # Models will go to `/classroom_resources/3dmodels/`

class ThreeDModel(models.Model):
    name = models.CharField(max_length=255)
    model_file = models.FileField(upload_to=model_upload_path)  # ✅ Custom Upload Path
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
