from django.db import models

# Create your models here.
class Flashcard(models.Model):
    #title = models.CharField(max_length=100)
    #content = models.TextField()
    file = models.FileField(upload_to='flashcards/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.file.name)

class GeneratedFlashcard(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name="generated_flashbacks")
    topic = models.CharField(max_length=255)
    summary = models.TextField()

    def __str__(self):
        return self.topic