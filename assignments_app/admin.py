from django.contrib import admin
from .models import Assignment, Question, MCQOptions, Submission, Remark, Notification

class MCQOptionInline(admin.TabularInline):
    model = MCQOptions
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text','assignment','is_mcq']
    list_filter = ['is_mcq']
    search_fields = ['text','assignment__name']
    inlines = [MCQOptionInline]

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['name','instructor','group','deadline']
    list_filter = ['deadline','group']
    search_fields = ['name','instructor__username']

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment','student','submitted_at']
    list_filter = ['assignment']
    search_fields = ['assignment__name','student__username']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['student','message','created_at','is_read']
    list_filter = ['student','is_read']
    search_fields = ['student','created_at']

admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Remark)
admin.site.register(Notification, NotificationAdmin)