from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from .forms import ResourceForm, CategoryForm
from .models import Resource, Category
from django.contrib import messages
from django.views.decorators.http import require_POST
import os
from django.db import models
from classroom.models import Classroom


def home(request):
    personal_folders = Category.objects.filter(owner=request.user)
    
    classroom_folders = Category.objects.filter(
        classroom__in=Classroom.objects.filter(
            models.Q(instructor=request.user) |
            models.Q(students=request.user)
        )
    )

    categories = (personal_folders | classroom_folders).order_by('id').distinct()
    
    return render(request, 'resource_library/home.html', {'categories': categories})


@require_POST
@require_POST
@require_POST
def delete_folder(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # CASE 1: Instructor can delete classroom folders or their own personal folder
    if request.user.role == "Instructor":
        if category.owner is None or category.owner == request.user:
            pass  # allow
        else:
            messages.error(request, "You can't delete folders owned by others.")
            return redirect('resource_library:home')

    # CASE 2: Student can only delete their own personal folder
    elif request.user.role == "Student" and category.owner == request.user:
        pass  # allow

    else:
        messages.error(request, "You are not allowed to delete this folder.")
        return redirect('resource_library:home')

    # Prevent deletion if resources exist
    if category.resource_set.exists():
        messages.error(request, "Cannot delete folder with resources inside. Please delete resources first.")
        return redirect('resource_library:home')

    category.delete()
    messages.success(request, "Folder deleted successfully.")
    return redirect('resource_library:home')



def add_folder(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user  # Assign the logged-in user as the owner
            category.save()
            return redirect('resource_library:home')
    else:
        form = CategoryForm()
    return render(request, 'resource_library/add_folder.html', {'form': form})


def resource_upload(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.save()
            return redirect('resource_library:resource_list', category_name=resource.category.name)
    else:
        form = ResourceForm(user=request.user)

    return render(request, 'resource_library/upload_resource.html', {'form': form})


def resource_list(request, category_name):
    user = request.user

    # 1. Try to get a personal folder with this name owned by this user
    personal_folder = Category.objects.filter(name=category_name, owner=user).first()
    if personal_folder:
        category = personal_folder
    else:
        # 2. Try to get a classroom folder with this name (owner=None)
        classroom_folder = Category.objects.filter(name=category_name, owner__isnull=True).first()
        if not classroom_folder:
            raise Http404("No such category found.")

        classroom = getattr(classroom_folder, 'classroom', None)
        if not classroom:
            raise Http404("Classroom folder is misconfigured.")

        if user != classroom.instructor and user not in classroom.students.all():
            raise Http404("You do not have permission to access this classroom folder.")

        category = classroom_folder

    # 4. Fetch resources
    search_query = request.GET.get("q", "")
    resources = Resource.objects.filter(category=category)
    if search_query:
        resources = resources.filter(title__icontains=search_query)

    return render(request, 'resource_library/resource_list.html', {
        'resources': resources.order_by('-uploaded_at'),
        'category_name': category.name,
        'category': category,             # ← Pass full category object
        'search_query': search_query,
        'user_role': user.role            # ← Pass user role for conditionals
    })



def resource_download(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)  # 👈 Check ownership
    file_path = resource.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(resource.file.name))
    else:
        raise Http404("File not found")

def resource_delete(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    if request.user != resource.user and request.user.role != "Instructor":
        messages.error(request, "You are not allowed to delete this resource.")
        return redirect('resource_library:resource_list', category_name=resource.category.name)

    category_name = resource.category.name if resource.category else "Uncategorized"
    resource.delete()
    return redirect('resource_library:resource_list', category_name=category_name)
