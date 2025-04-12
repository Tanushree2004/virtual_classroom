from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Exam, ExamSubmission, ExamMCQOptions, ExamQuestion
from django.utils import timezone
from .forms import ExamForm
from django.http import JsonResponse
import os
from datetime import datetime
from classroom.models import Classroom
from django.utils.timezone import make_aware

@login_required
def instructor_dashboard_exam(request):
    if request.user.role.lower() != 'instructor':
        return render(request, 'exam/error_asg.html', {
            'message':'Access Denied'
            })
    
    exams = Exam.objects.filter(instructor = request.user)
    now = timezone.now()
    return render(request, 'exam/instructor_dashboard_exam.html',{
        'exams':exams, 
        'now':now
        })

@login_required
def student_dashboard_exam(request):
    if request.user.role.lower() != 'student':
        return render(request, 'error.html', {
            'message': 'Access Denied'
        })
    classroom_titles = Classroom.objects.filter(
        students=request.user
    ).values_list('title', flat=True)
    exams = Exam.objects.filter(group__in = classroom_titles)
    submissions = ExamSubmission.objects.filter(student = request.user)
    now = timezone.now()
    submitted_ids = submissions.values_list('exam_id', flat=True)

    """now_date=now.date()
    now_time=now.date()
    live_exams = Exam.objects.filter(
        deadline = now_date,
        start_duration__lte = now_time
    )
    unseen_live_exams = live_exams.exclude(seen_by=request.user)
    for exam in unseen_live_exams:
        exam.seen_by.add(request.user)
    live_unseen_ids = [e.id for e in unseen_live_exams]"""
    live_exams = []
    for exam in exams:
        start_dt = make_aware(datetime.combine(exam.deadline, exam.start_duration))
        end_dt = make_aware(datetime.combine(exam.deadline, exam.end_duration))
        if start_dt <= now <= end_dt:
            live_exams.append(exam)

    unseen_live_exams = [exam for exam in live_exams if request.user not in exam.seen_by.all()]

    for exam in unseen_live_exams:
        exam.seen_by.add(request.user)

    live_unseen_ids = [e.id for e in unseen_live_exams]

    return render(request, 'exam/student_dashboard_exam.html',{
        'exams':exams,
        'submitted_ids': submitted_ids,
        'now':now,
        'has_unseen_live_exam' : bool(unseen_live_exams),
        'live_unseen_ids':live_unseen_ids,
    })

@login_required
def dashboard_redirect_exam(request):
    if request.user.role.lower() == 'instructor':
        return redirect('exam:instructor_dashboard_exam')
    elif request.user.role.lower() == 'student':
        return redirect('exam:student_dashboard_exam')
    else:
        return redirect('/')
    
@login_required
def create_exam(request):
    if request.user.role.lower() != 'instructor':
        return render(request, 'error_exam.html', {'message': 'Access Denied'})
    classrooms = Classroom.objects.filter(instructor = request.user)
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.instructor = request.user
            exam.save()  
            return redirect('exam:add_questions_exam', exam_id=exam.id)  # ✅ Pass correct ID

    else:
        form = ExamForm()

    return render(request, 'exam/create_exam.html', {'form': form, 'exam':None, 'classrooms':classrooms})


@login_required
def add_questions_exam(request, exam_id): 
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    if request.method == "POST":
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        is_mcq = True if question_type == "MCQ" else False

        if question_text and question_type:
            question = ExamQuestion.objects.create(
                exam=exam,  
                text=question_text,
                is_mcq = is_mcq
            )

            if is_mcq:
                options = request.POST.getlist('options[]')
                correct_option_ids = request.POST.getlist('correct_options[]') or []

                print("\n🟢 DEBUGGING DATA:")
                print("➡️  Options received:", options)
                print("➡️  Correct options received:", correct_option_ids)

                for i, option_text in enumerate(options):
                    is_correct = option_text in correct_option_ids
                    print(f"🔵 Saving: {option_text}, Index: {i}, Is Correct: {is_correct}")
                    ExamMCQOptions.objects.create(
                        question=question,
                        text=option_text,
                        is_correct= is_correct
                    )

            return redirect('exam:add_questions_exam', exam_id=exam.id)
    
    questions = ExamQuestion.objects.filter(exam=exam)
    return render(request, 'exam/add_questions_exam.html', {
        'exam': exam,
        'questions' : questions
        })

@login_required
def edit_question_exam(request, question_id):
    question = get_object_or_404(ExamQuestion, id=question_id)

    if request.user != question.exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        question_type = request.POST.get("question_type")
        is_mcq = question_type == "MCQ"

        # ✅ Update question text & type
        question.text = question_text
        question.is_mcq = is_mcq
        question.save()

        # ✅ Handle MCQ options update
        if is_mcq:
            options = request.POST.getlist("options[]")
            correct_options = request.POST.getlist("correct_options[]") or []

            # ✅ Clear old options & add updated ones
            ExamMCQOptions.objects.filter(question=question).delete()
            for i, option_text in enumerate(options):
                ExamMCQOptions.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=i in map(int, correct_options)
                )

        return redirect('exam:add_questions_exam', exam_id=question.exam.id)  # ✅ Redirect back

    exam = question.exam
    questions = ExamQuestion.objects.filter(exam=exam)  # ✅ Fetch existing questions

    return render(request, 'exam/add_questions_exam.html', {
        'exam': exam,
        'questions': questions,
        'editing_question': question  # ✅ Send question data for editing
    })


@login_required
def delete_question_exam(request, question_id):
    question = get_object_or_404(ExamQuestion, id=question_id)

    if request.user != question.exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    exam_id = question.exam.id
    question.delete()

    return redirect('exam:add_questions_exam', exam_id=exam_id)

@login_required
def finalize_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    return redirect('exam:instructor_dashboard_exam')  

@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    exam.delete()
    return redirect('exam:instructor_dashboard_exam')  

@login_required
def extend_deadline_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    if request.method == "POST":
        new_deadline = request.POST.get("new_deadline")
        if new_deadline:
            exam.deadline = new_deadline
            exam.save()  # ✅ Update deadline
            return redirect('exam:instructor_dashboard_exam')  # ✅ Redirect to dashboard after update

    return render(request, 'exam/extend_deadline_exam.html', {'exam': exam})

@login_required
def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user.role.lower() != 'student':
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    questions = ExamQuestion.objects.filter(exam=exam)
    mcq_score = 0
    total_mcq = 0
    mcq_answers = {}
    descriptive_answers = {}
    #now = datetime.now()
    now = timezone.now()
    """duration = (
        datetime.combine(exam.deadline, exam.end_duration)- max(datetime.combine(exam.deadline, exam.start_duration),now)
    ).total_seconds()"""
    
    exam_start_datetime = make_aware(datetime.combine(exam.deadline, exam.start_duration))
    exam_started = now >= exam_start_datetime
    exam_end_datetime = make_aware(datetime.combine(exam.deadline, exam.end_duration))
    exam_end = now >= exam_end_datetime
    duration = (exam_end_datetime - max(exam_start_datetime,now)).total_seconds()
    if request.method == "POST":
        for question in questions:
            if question.is_mcq:
                total_mcq += 1
                selected_options = request.POST.getlist(f'question_{question.id}')
                selected_options = set(map(int, selected_options)) if selected_options else set()
                mcq_answers[str(question.id)] = list(selected_options)
                correct_options = set(ExamMCQOptions.objects.filter(question=question, is_correct=True).values_list('id', flat=True))
                if selected_options == correct_options:
                    mcq_score += 1
                elif selected_options.intersection(correct_options):
                    mcq_score += len(selected_options.intersection(correct_options))/len(correct_options)

            else:
                answer_text = request.POST.get(f'question_{question.id}_text')
                answer_files = request.FILES.getlist(f'question_{question.id}_files')

                if answer_text and answer_files:
                    return render(request, 'exam/error_exam.html', {'message': 'Cannot submit both text and file!'})

                uploaded_file_urls = []
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'examuploads')
                os.makedirs(upload_dir, exist_ok=True)
                for file in answer_files:
                    safe_name=file.name.replace('#','_')
                    file_path = os.path.join('examuploads', safe_name)  
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
        submission = ExamSubmission.objects.create(
            exam=exam,
            student=request.user,
            mcq_answers=mcq_answers,
            descriptive_answers=descriptive_answers
        )

        return render(request, 'exam/submission_complete_exam.html', {
            'exam': exam,
            'mcq_score': mcq_score,
            'total_mcq': total_mcq
        })

    return render(request, 'exam/submit_exam.html', {
        'exam': exam,
        'questions': questions,
        "duration_seconds": int(duration),
        'exam_started': exam_started,
        'exam_end': exam_end,
    })

@login_required
def view_submissions_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    submissions = ExamSubmission.objects.filter(exam=exam)

    return render(request, 'exam/view_submissions_exam.html', {
        'exam': exam,
        'submissions': submissions,
    })

@login_required
def view_student_submission_exam(request, submission_id):
    submission = get_object_or_404(ExamSubmission, id=submission_id)

    if request.user != submission.exam.instructor:
        return render(request, 'exam/error_exam.html', {'message': 'Access Denied'})

    exam = submission.exam
    questions = ExamQuestion.objects.filter(exam=exam)
    mcq_score = 0
    total_mcq = 0
    formatted_answers = []

    for idx, question in enumerate(questions, start=1):
        answer_data = {
            "index": idx,
            "question_text": question.text,
            "is_mcq": question.is_mcq,
        }

        if question.is_mcq:
            total_mcq += 1
            selected_options = submission.mcq_answers.get(str(question.id), [])  # ✅ Retrieve selected MCQ answer(s)
            correct_options = set(
                ExamMCQOptions.objects.filter(question=question, is_correct=True).values_list("id", flat=True)
            )

            selected_options = set(map(str, selected_options)) if selected_options else set()  # ✅ Ensure both sides are strings
            correct_options = set(map(str, correct_options))  # ✅ Convert correct options to strings too

            answer_data["selected_options"] = list(ExamMCQOptions.objects.filter(id__in=selected_options).values_list("text", flat=True))  # ✅ Store text of selected options
            answer_data["correct_options"] = list(ExamMCQOptions.objects.filter(id__in=correct_options).values_list("text", flat=True))  # ✅ Store text of correct options
            answer_data["is_correct"] = selected_options == correct_options  # ✅ Compare selections properly

            if selected_options == correct_options:
                mcq_score += 1
            elif selected_options.intersection(correct_options):
                mcq_score += len(selected_options.intersection(correct_options))/len(correct_options)

        else:
            descriptive_answer = submission.descriptive_answers.get(str(question.id),{})
            answer_data["descriptive_text"] = descriptive_answer.get("text","")
            answer_data["files"] = descriptive_answer.get("files",[])

        formatted_answers.append(answer_data)

    return render(request, 'exam/view_student_submission_exam.html', {
        'submission': submission,
        'exam': exam,
        'formatted_answers': formatted_answers,
        'mcq_score': mcq_score,
        'total_mcq': total_mcq,
    })

