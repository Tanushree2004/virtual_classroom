from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from .forms import ResourceForm, CategoryForm
from .models import Resource, Category
from django.contrib import messages
from django.views.decorators.http import require_POST
import os

def home(request):
    # Get all categories (folders) from the database.
    categories = Category.objects.all()
    return render(request, 'resource_library/home.html', {'categories': categories})

@require_POST
def delete_folder(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Optional: Prevent deletion if resources exist in this category
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
            form.save()
            # Redirect back to home after folder creation.
            return redirect('resource_library:home')
    else:
        form = CategoryForm()
    return render(request, 'resource_library/add_folder.html', {'form': form})

def resource_upload(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save()
            # Redirect to the resource list for the selected folder.
            resource.user = request.user  # 👈 Link to logged-in user
            resource.save()
            return redirect('resource_library:resource_list', category_name=resource.category.name)
    else:
        form = ResourceForm()
    return render(request, 'resource_library/upload_resource.html', {'form': form})

def resource_list(request, category_name):
    # Find the category by name.
    category = get_object_or_404(Category, name=category_name)
    search_query = request.GET.get("q", "")
    if search_query:
        resources = Resource.objects.filter(
            category=category,
            user=request.user,  # 👈 Only user's uploads
            title__icontains=search_query
        ).order_by('-uploaded_at')
    else:
        resources = Resource.objects.filter(
            category=category,
            user=request.user  # 👈 Only user's uploads
        ).order_by('-uploaded_at')
    context = {
        'resources': resources,
        'category_name': category.name,
        'search_query': search_query,  # Pass the query so we can show it in the input.
    }
    return render(request, 'resource_library/resource_list.html', context)

def resource_download(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)  # 👈 Check ownership
    file_path = resource.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(resource.file.name))
    else:
        raise Http404("File not found")

def resource_delete(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)  # 👈 Check ownership
    category_name = resource.category.name if resource.category else "Uncategorized"
    resource.delete()
    return redirect('resource_library:resource_list', category_name=category_name)
