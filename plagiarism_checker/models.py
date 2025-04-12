from django.db import models

class PlagiarismCheck(models.Model):
    file1 = models.FileField(upload_to='plagiarism_files/')
    file2 = models.FileField(upload_to='plagiarism_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plagiarism Check {self.id}"
