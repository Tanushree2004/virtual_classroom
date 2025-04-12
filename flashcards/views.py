from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Flashcard, GeneratedFlashcard
from .forms import FlashcardForm
from django.http import HttpResponse
from django.conf import settings
import os
from .utils import generate_flashcards
import json
from django.core.serializers import serialize
from django.utils.safestring import mark_safe
import re

# Create your views here.
def upload_file(request):
    if request.method == 'POST':
        form = FlashcardForm(request.POST, request.FILES)
        if form.is_valid():
            flashcard = form.save()
            return JsonResponse({'message': 'File uploaded successfully', 'file': flashcard.file.url})
        return JsonResponse({'error': form.errors}, status=400)
    return render(request, 'flashcards/flashcard.html')

def test_base_dir(request):
    return HttpResponse(f"BASE_DIR: {settings.BASE_DIR}")

def check_file_path(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'flashcards', 'DS-Forouzan.pdf')

    if os.path.exists(file_path):
        return HttpResponse(f"File exists at: {file_path}")
    else:
        return HttpResponse("File not found", status=404)

def process_flashcards(request):
    try:
        latest_file = Flashcard.objects.latest("uploaded_at")
    except Flashcard.DoesNotExist:
        return HttpResponse("No flashcards found.", status=404)
    file_path = os.path.join(settings.MEDIA_ROOT, str(latest_file.file))
    flashcards = generate_flashcards(file_path)
    if not flashcards:
        return HttpResponse("No flashcards generated.", status=400)
    for card in flashcards:
        if "question" and "answer" in card:
            cleaned_question = re.sub(r"\*\*Card \d+:\*\*", "", card["question"]).strip()
            cleaned_answer = re.sub(r"\*\*Card \d+:\*\*", "", card["answer"]).strip()
            GeneratedFlashcard.objects.create(
            flashcard=latest_file,
            topic=cleaned_question,  # Storing question in 'topic'
            summary=cleaned_answer    # Storing answer in 'summary'
            )
        else:
            print("Invalid card format")
    return HttpResponse(latest_file.id)

def show_flashcards(request, file_id):
    flashcards = GeneratedFlashcard.objects.filter(flashcard_id=file_id)
    if not flashcards.exists():
        return HttpResponse("No flashcards available", status=400)

    return render(request, "flashcards/show_flashcards.html", {"flashcards": flashcards})
