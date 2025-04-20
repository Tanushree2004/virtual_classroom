from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Assignment, Submission, MCQOptions, Question, Remark, Notification
from django.utils import timezone
from .forms import AssignmentForm
from django.http import JsonResponse
import os
from classroom.models import Classroom

@login_required
def instructor_dashboard_asg(request):
    if request.user.role.lower() != 'instructor':
        return render(request, 'assignments_app/error_asg.html', {
            'message':'Access Denied'
            })
    assignments = Assignment.objects.filter(instructor = request.user)
    now = timezone.now()
    return render(request, 'assignments_app/instructor_dashboard_asg.html',{
        'assignments':assignments, 
        'now':now
        })

@login_required
def student_dashboard_asg(request):
    if request.user.role.lower() != 'student':
        return render(request, 'error.html', {
            'message': 'Access Denied'
        })
    classroom_titles = Classroom.objects.filter(
        students=request.user
    ).values_list('title', flat=True)
    assignments = Assignment.objects.filter(group__in=classroom_titles)
    submissions = Submission.objects.filter(student = request.user)
    now = timezone.now()
    submitted_ids = submissions.values_list('assignment_id', flat=True)
    return render(request, 'assignments_app/student_dashboard_asg.html',{
        'assignments':assignments,
        'submitted_ids': submitted_ids,
        'now':now
    })

@login_required
def dashboard_redirect_asg(request):
    if request.user.role.lower() == 'instructor':
        return redirect('assignments_app:instructor_dashboard_asg')
    elif request.user.role.lower() == 'student':
        return redirect('assignments_app:student_dashboard_asg')
    else:
        return redirect('/')
    
@login_required
def create_assignment(request):
    if request.user.role.lower() != 'instructor':
        return render(request, 'error_asg.html', {'message': 'Access Denied'})

    classrooms = Classroom.objects.filter(instructor = request.user)
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.instructor = request.user
            assignment.save()  # ✅ Ensure assignment is saved before redirecting
            return redirect('assignments_app:add_questions', assignment_id=assignment.id)  # ✅ Pass correct ID

    else:
        form = AssignmentForm()
    now = timezone.localtime()
    formatted_now = now.strftime('%Y-%m-%dT%H:%M')

    return render(request, 'assignments_app/create_assignment.html', {'form': form, 'assignment':None, 'classrooms':classrooms, 'now': formatted_now,})


@login_required
def add_questions(request, assignment_id):  # Expect assignment_id from URL
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    if request.method == "POST":
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        is_mcq = True if question_type == "MCQ" else False
        question_attachment = request.FILES.get('question_attachment')

        #print("FILES:", request.FILES)

        if question_text and question_type:
            question = Question.objects.create(
                assignment=assignment,  # Link question to the assignment
                text=question_text,
                is_mcq = is_mcq,
                question_attachment = question_attachment
            )

            if is_mcq:
                options = request.POST.getlist('options[]')
                correct_option_ids = request.POST.getlist('correct_options[]') or []

                #print("\n DEBUGGING DATA:")
                #print(" Options received:", options)
                #print(" Correct options received:", correct_option_ids)

                for i, option_text in enumerate(options):
                    is_correct = option_text in correct_option_ids
                    #print(f" Saving: {option_text}, Index: {i}, Is Correct: {is_correct}")
                    MCQOptions.objects.create(
                        question=question,
                        text=option_text,
                        is_correct= is_correct
                    )

            return redirect('assignments_app:add_questions', assignment_id=assignment.id)
    
    questions = Question.objects.filter(assignment=assignment)
    return render(request, 'assignments_app/add_questions.html', {
        'assignment': assignment,
        'questions' : questions
        })

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question_attachment = None

    if request.user != question.assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        question_type = request.POST.get("question_type")
        is_mcq = question_type == "MCQ"
        question_attachment = request.FILES.get('question_attachment')
        #attachment_url = question.question_attachment.url if question.question_attachment else None

        # ✅ Update question text & type
        question.text = question_text
        question.is_mcq = is_mcq
        if request.POST.get("remove_attachment") == "1":
            if question.question_attachment:
                question.question_attachment.delete(save=False)
                question.question_attachment = None

        # If new attachment was uploaded
        if question_attachment:
            question.question_attachment = question_attachment
        question.save()

        # ✅ Handle MCQ options update
        if is_mcq:
            options = request.POST.getlist("options[]")
            correct_option_ids = request.POST.getlist("correct_options[]") or []

            # ✅ Clear old options & add updated ones
            #MCQOptions.objects.filter(question=question).delete()
            question.options.all().delete()
            for i, option_text in enumerate(options):
                is_correct = option_text in correct_option_ids
                MCQOptions.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=is_correct
                )

        return redirect('assignments_app:add_questions', assignment_id=question.assignment.id)  # ✅ Redirect back

    assignment = question.assignment
    questions = Question.objects.filter(assignment=assignment)  # ✅ Fetch existing questions
    existing_options = question.options.all() if question.is_mcq else []

    #checked_options = [option.id for option in existing_options if option.is_correct]
    return render(request, 'assignments_app/add_questions.html', {
        'assignment': assignment,
        'questions': questions,
        'editing_question': question,  # ✅ Send question data for editing
        #'attachment_url': attachment_url,
        'existing_options': existing_options,
        'question_attachment': question_attachment,
    })


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.user != question.assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    assignment_id = question.assignment.id
    question.delete()

    return redirect('assignments_app:add_questions', assignment_id=assignment_id)

@login_required
def finalize_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    # Assignment is already saved, just mark it as "Live" if needed

    return redirect('assignments_app:instructor_dashboard_asg')  # Redirect to dashboard

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    assignment.delete()
    return redirect('assignments_app:instructor_dashboard_asg')  # ✅ Redirect back after deletion

@login_required
def extend_deadline(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    if request.method == "POST":
        new_deadline = request.POST.get("new_deadline")
        if new_deadline:
            assignment.deadline = new_deadline
            assignment.save()  # ✅ Update deadline
            return redirect('assignments_app:instructor_dashboard_asg')  # ✅ Redirect to dashboard after update

    return render(request, 'assignments_app/extend_deadline.html', {'assignment': assignment})

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user.role.lower() != 'student':
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    questions = Question.objects.filter(assignment=assignment)
    mcq_score = 0
    total_mcq = 0
    mcq_answers = {}
    descriptive_answers = {}

    if request.method == "POST":
        for question in questions:
            if question.is_mcq:
                total_mcq += 1
                selected_options = request.POST.getlist(f'question_{question.id}')
                selected_options = set(map(int, selected_options)) if selected_options else set()
                mcq_answers[str(question.id)] = list(selected_options)
                correct_options = set(MCQOptions.objects.filter(question=question, is_correct=True).values_list('id', flat=True))
                if selected_options == correct_options:
                    mcq_score += 1
                elif selected_options.intersection(correct_options):
                    mcq_score += len(selected_options.intersection(correct_options))/len(correct_options)

            else:
                answer_text = request.POST.get(f'question_{question.id}_text')
                answer_files = request.FILES.getlist(f'question_{question.id}_files')

                uploaded_file_urls = []
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                for file in answer_files:
                    safe_name=file.name.replace('#','_')
                    file_path = os.path.join('uploads', safe_name)  
                    full_path=os.path.join(settings.MEDIA_ROOT, file_path)
                    with open(full_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    uploaded_file_urls.append(file_path)
                descriptive_answers[str(question.id)] = {
                    "text": answer_text if answer_text else None,
                    "files": uploaded_file_urls if uploaded_file_urls else []  # ✅ Save actual file URLs
                }

        # ✅ Save submission with correctly structured data
        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            mcq_answers=mcq_answers,
            descriptive_answers=descriptive_answers
        )

        return render(request, 'assignments_app/submission_complete.html', {
            'assignment': assignment,
            'mcq_score': mcq_score,
            'total_mcq': total_mcq
        })

    return render(request, 'assignments_app/submit_assignment.html', {
        'assignment': assignment,
        'questions': questions
    })

@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    submissions = Submission.objects.filter(assignment=assignment)

    return render(request, 'assignments_app/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })

@login_required
def view_student_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.user != submission.assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    assignment = submission.assignment
    questions = Question.objects.filter(assignment=assignment)
    mcq_score = 0
    total_mcq = 0
    formatted_answers = []

    for idx, question in enumerate(questions, start=1):
        answer_data = {
            "index": idx,
            "question_text": question.text,
            "is_mcq": question.is_mcq,
            "attachments": question.question_attachment,
        }

        if question.is_mcq:
            total_mcq += 1
            selected_options = submission.mcq_answers.get(str(question.id), [])  # Retrieve selected MCQ answer(s)
            correct_options = set(
                MCQOptions.objects.filter(question=question, is_correct=True).values_list("id", flat=True)
            )

            selected_options = set(map(str, selected_options)) if selected_options else set()  # Ensure both sides are strings
            correct_options = set(map(str, correct_options))  # Convert correct options to strings too

            answer_data["selected_options"] = list(MCQOptions.objects.filter(id__in=selected_options).values_list("text", flat=True))  # ✅ Store text of selected options
            answer_data["correct_options"] = list(MCQOptions.objects.filter(id__in=correct_options).values_list("text", flat=True))  # ✅ Store text of correct options
            answer_data["is_correct"] = selected_options == correct_options  # Compare selections properly

            if selected_options == correct_options:
                mcq_score += 1
            elif selected_options.intersection(correct_options):
                mcq_score += len(selected_options.intersection(correct_options))/len(correct_options)
        else:
            descriptive_answer = submission.descriptive_answers.get(str(question.id),{})
            answer_data["descriptive_text"] = descriptive_answer.get("text","")
            answer_data["files"] = descriptive_answer.get("files",[])
            
        formatted_answers.append(answer_data)

    return render(request, 'assignments_app/view_student_submission.html', {
        'submission': submission,
        'assignment': assignment,
        'formatted_answers': formatted_answers,
        'mcq_score': mcq_score,
        'total_mcq': total_mcq,
    })

@login_required
def add_remark(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.user != submission.assignment.instructor:
        return render(request, 'assignments_app/error_asg.html', {'message': 'Access Denied'})

    if request.method == "POST":
        remark_text = request.POST.get("remark")
        if remark_text:
            remark = Remark.objects.create(
                submission=submission,
                text=remark_text,
                given_at=timezone.now()
            )

            # Create a notification using the `Remark.text` field
            Notification.objects.create(
                student=submission.student,
                message=f"New remark for your submission on {submission.assignment.name}: {remark.text}"
            )

            return redirect('assignments_app:view_submissions', assignment_id=submission.assignment.id)

    return render(request, 'assignments_app/add_remark.html', {'submission': submission})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)

    if request.method == "POST":
        notification.is_read = True
        notification.save()

    return redirect('assignments_app:student_dashboard_asg')

@login_required
def details_asg(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = Question.objects.filter(assignment=assignment)


    return render(request, 'assignments_app/details_asg.html',
                  {'assignment':assignment,
                   'questions':questions,
                   })

@login_required
def submission_details(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(Submission, assignment=assignment, student=request.user)
    questions = assignment.questions.all()
    context = {
        'submission': submission,
        'assignment': assignment,
        'questions' : questions,
    }
    return render(request, 'assignments_app/submission_details.html', context)