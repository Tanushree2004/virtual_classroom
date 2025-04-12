from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.storage import default_storage
import os
from .models import Classroom, ClassroomResource
from .forms import ClassroomForm, ClassroomResourceForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .forms import InviteStudentForm
from django.db.models import Q

@login_required
def classroom_list(request):
    user = request.user
    if user.role == "Admin":
        classrooms = Classroom.objects.filter(instructor__institution=user.institution)
    elif user.role == "Instructor":
        classrooms = Classroom.objects.filter(instructor=user, instructor__institution=user.institution)
    elif user.role == "Student":
        classrooms = Classroom.objects.filter(students=user, instructor__institution=user.institution)
    else:
        classrooms = Classroom.objects.none()  

    return render(request, 'classroom/classroom_list.html', {'classrooms': classrooms})

@login_required
def create_classroom(request):
    if request.method == 'POST':
        form = ClassroomForm(request.POST, user=request.user)  
        if form.is_valid():
            classroom = form.save(commit=False)

            if classroom.instructor.institution != request.user.institution:
                messages.error(request, "You can only assign instructors from your institution.")
                return redirect('create_classroom')

            classroom.save()
            form.save_m2m() 
            return redirect('classroom_list')
    else:
        form = ClassroomForm(user=request.user)  

    return render(request, 'classroom/create_classroom.html', {'form': form})


@login_required
def edit_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if classroom.instructor.institution != request.user.institution:
        messages.error(request, "You do not have permission to edit this classroom.")
        return redirect('classroom_list')

    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=classroom, user=request.user)  # Pass user
        if form.is_valid():
            updated_classroom = form.save(commit=False)
            if updated_classroom.instructor.institution != request.user.institution:
                messages.error(request, "You can only assign instructors from your institution.")
                return redirect('edit_classroom', classroom_id=classroom.id)

            updated_classroom.save()
            form.save_m2m()
            return redirect('classroom_list')
    else:
        form = ClassroomForm(instance=classroom, user=request.user) 

    return render(request, 'classroom/edit_classroom.html', {'form': form})

@login_required
def delete_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if classroom.instructor.institution != request.user.institution:
        messages.error(request, "You do not have permission to delete this classroom.")
        return redirect('classroom_list')

    classroom.delete()
    messages.success(request, "Classroom deleted successfully.")
    return redirect('classroom_list')

User = get_user_model()

@login_required
def invite_student(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if classroom.instructor.institution != request.user.institution:
        messages.error(request, "You cannot invite students from another institution.")
        return redirect('classroom_list')

    if request.method == 'POST':
        form = InviteStudentForm(request.POST, institution=request.user.institution)  
        if form.is_valid():
            student = form.cleaned_data['student']
            if student.institution != request.user.institution:
                messages.error(request, "You can only invite students from your institution.")
                return redirect('classroom_list')

            if student in classroom.students.all():
                messages.warning(request, f'{student.username} is already in {classroom.title}.')
            else:
                classroom.students.add(student)
                messages.success(request, f'{student.username} has been successfully added to {classroom.title}.')

            return redirect('classroom_list')
    else:
        form = InviteStudentForm(institution=request.user.institution)  

    return render(request, 'classroom/invite_student.html', {'form': form, 'classroom': classroom})
@login_required
def manage_resources(request, classroom_id):
    user = request.user
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if classroom.instructor.institution != request.user.institution:
        messages.error(request, "You do not have permission to manage resources for this classroom.")
        return redirect('classroom_list')

    resources = ClassroomResource.objects.filter(classroom=classroom)

    if request.method == 'POST':
        form = ClassroomResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.classroom = classroom
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('manage_resources', classroom_id=classroom.id)
    else:
        form = ClassroomResourceForm()

    return render(request, 'classroom/manage_resources.html', {
        'classroom': classroom,
        'resources': resources,
        'form': form
    })

@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(ClassroomResource, id=resource_id)
    if resource.classroom.instructor.institution != request.user.institution:
        messages.error(request, "You do not have permission to delete this resource.")
        return redirect('classroom_list')

    resource.delete()
    messages.success(request, 'Resource deleted successfully!')
    return redirect('manage_resources', classroom_id=resource.classroom.id)

@login_required
def serve_resource(request, filename):
    file_path = os.path.join('classroom_resources', filename)
    try:
        resource = ClassroomResource.objects.get(file=filename)
        if resource.classroom.instructor.institution != request.user.institution:
            messages.error(request, "You do not have permission to access this resource.")
            return redirect('classroom_list')
    except ClassroomResource.DoesNotExist:
        raise Http404("File not found.")

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/msword')
    else:
        raise Http404("File not found.")
