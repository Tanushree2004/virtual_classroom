from django.contrib import admin
from .models import Flashcard, GeneratedFlashcard
# Register your models here.

@admin.register(Flashcard)

class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('id','file','uploaded_at')

    def file_link(self, obj):
        if obj.file:
            return f'<a href="{obj.file.url}" target="_blank">{obj.file.name}</a>'
        return "(No file)"
    file_link.allow_tags = True
    file_link.short_description = 'File'

@admin.register(GeneratedFlashcard)
class GeneratedFlashcardAdmin(admin.ModelAdmin):
    list_display = ('id','flashcard','topic','summary')