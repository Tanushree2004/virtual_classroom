from django.contrib import admin
from .models import Exam, ExamMCQOptions, ExamQuestion, ExamSubmission

class MCQOptionInline(admin.TabularInline):
    model = ExamMCQOptions
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text','exam','is_mcq']
    list_filter = ['is_mcq']
    search_fields = ['text','exam__name']
    inlines = [MCQOptionInline]

class ExamAdmin(admin.ModelAdmin):
    list_display = ['name','instructor','group','deadline','start_duration','end_duration']
    list_filter = ['deadline','group']
    search_fields = ['name','instructor__username']

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['exam','student','submitted_at']
    list_filter = ['exam']
    search_fields = ['exam__name','student__username']

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamQuestion, QuestionAdmin)
admin.site.register(ExamSubmission, SubmissionAdmin)
