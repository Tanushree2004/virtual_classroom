from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Whiteboard
import json
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt

def dashboard(request):
    boards = Whiteboard.objects.filter(user=request.user)
    return render(request, "whiteboard/dashboard.html", {"boards": boards})

def create_whiteboard(request):
    if request.method == "POST":
        title = request.POST.get("title")
        background = request.POST.get("background", "#ffffff")
        board = Whiteboard.objects.create(user=request.user, title=title)
        return redirect("whiteboard:edit_whiteboard", board.id)

    return render(request, "whiteboard/create_whiteboard.html")

def edit_whiteboard(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, user=request.user)
    image_url = board.image.url if board.image and board.image.name else ""
    return render(request, "whiteboard/editor.html", {"board": board, "image_url": image_url})

@csrf_exempt
def save_whiteboard(request, board_id):
    if request.method == "POST":
        board = get_object_or_404(Whiteboard, id=board_id, user=request.user)
        image_data = request.POST.get("image")
        
        if image_data:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            board.image.save(f"whiteboard_{board.id}.{ext}", ContentFile(base64.b64decode(imgstr)), save=True)
        
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error"}, status=400)

def delete_whiteboard(request, board_id):
    board = get_object_or_404(Whiteboard, id=board_id, user=request.user)
    board.delete()
    return redirect("whiteboard:dashboard")
