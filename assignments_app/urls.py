from django.urls import path
from .views import instructor_dashboard_asg, student_dashboard_asg, dashboard_redirect_asg, create_assignment, add_questions,edit_question,delete_question, finalize_assignment, delete_assignment, extend_deadline, submit_assignment, view_student_submission, view_submissions, add_remark, mark_notification_read
from django.conf import settings
from django.conf.urls.static import static

app_name = "assignments_app"
    
urlpatterns = [
    path('', dashboard_redirect_asg, name="dashboard_redirect_asg"),
    path('instructor_asg/', instructor_dashboard_asg, name="instructor_dashboard_asg"),
    path('student_asg/', student_dashboard_asg, name="student_dashboard_asg"),
    path('create_assignment/', create_assignment, name="create_assignment"),
    path('add_questions/<int:assignment_id>/', add_questions, name="add_questions"),
    path('edit_question/<int:question_id>/', edit_question, name="edit_question"),
    path('delete_question/<int:question_id>/', delete_question, name="delete_question"),
    path('finalize_assignment/<int:assignment_id>/', finalize_assignment, name="finalize_assignment"),
    path('delete_assignment/<int:assignment_id>/', delete_assignment, name="delete_assignment"),
    path('extend_deadline/<int:assignment_id>/', extend_deadline, name="extend_deadline"),
    path('submit_assignment/<int:assignment_id>/', submit_assignment, name="submit_assignment"),
    path('view_submissions/<int:assignment_id>/', view_submissions, name="view_submissions"),
    path('view_submission/<int:submission_id>/', view_student_submission, name="view_student_submission"),
    path('add_remark/<int:submission_id>/', add_remark, name="add_remark"),
    path('mark_notification_read/<int:notification_id>/', mark_notification_read, name="mark_notification_read"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)