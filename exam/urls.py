from django.urls import path
from .views import instructor_dashboard_exam, student_dashboard_exam, dashboard_redirect_exam, create_exam, add_questions_exam,edit_question_exam,delete_question_exam, finalize_exam, delete_exam, extend_deadline_exam, submit_exam, view_student_submission_exam, view_submissions_exam, details_exam, submission_details
from django.conf import settings
from django.conf.urls.static import static

app_name = "exam"
    
urlpatterns = [
    path('', dashboard_redirect_exam, name="dashboard_redirect_exam"),
    path('instructor_exam/', instructor_dashboard_exam, name="instructor_dashboard_exam"),
    path('student_exam/', student_dashboard_exam, name="student_dashboard_exam"),
    path('create_exam/', create_exam, name="create_exam"),
    path('add_questions_exam/<int:exam_id>/', add_questions_exam, name="add_questions_exam"),
    path('edit_question_exam/<int:question_id>/', edit_question_exam, name="edit_question_exam"),
    path('delete_question_exam/<int:question_id>/', delete_question_exam, name="delete_question_exam"),
    path('finalize_exam/<int:exam_id>/', finalize_exam, name="finalize_exam"),
    path('delete_exam/<int:exam_id>/', delete_exam, name="delete_exam"),
    path('extend_deadline_exam/<int:exam_id>/', extend_deadline_exam, name="extend_deadline_exam"),
    path('submit_exam/<int:exam_id>/', submit_exam, name="submit_exam"),
    path('view_submissions/<int:exam_id>/', view_submissions_exam, name="view_submissions_exam"),
    path('view_submission/<int:submission_id>/', view_student_submission_exam, name="view_student_submission_exam"),
    path('details_exam/<int:exam_id>/', details_exam, name="details_exam"),
    path('submission_details/<int:exam_id>/',submission_details, name="submission_details"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)