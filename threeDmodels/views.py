from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ThreeDModel
from .forms import ThreeDModelForm
import os

@login_required
def upload_3d_model(request):
    if request.method == "POST":
        form = ThreeDModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("threeDmodels:model_list")  # Redirect to the model list page
    else:
        form = ThreeDModelForm()

    return render(request, "upload_model.html", {"form": form})
@login_required
def model_list(request):
    models = ThreeDModel.objects.all()
    return render(request, "model_list.html", {"models": models})

@csrf_exempt
@login_required
def delete_model(request, model_id):
    model = get_object_or_404(ThreeDModel, id=model_id)
    model.delete()
    return redirect('threeDmodels:model_list')
        
