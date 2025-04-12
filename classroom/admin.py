from django.contrib import admin
from .models import ClassroomResource,Classroom

@admin.register(ClassroomResource)
class ClassroomResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'classroom', 'uploaded_by', 'uploaded_at']

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at')