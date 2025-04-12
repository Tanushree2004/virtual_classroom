from django.contrib import admin
from .models import Whiteboard

# Register your models here.
@admin.register(Whiteboard)
class WhiteboardAdmin(admin.ModelAdmin):
    list_display = ('title','user','created_at')
    search_fields = ('title','user__username')