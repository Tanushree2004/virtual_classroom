from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Meeting
from .utils import generate_hmac_id, generate_meeting_id
import uuid
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Meeting, Recording
from django.contrib.auth import get_user_model

@login_required
def lobby(request):
    user_name = request.user.username
    return render(request, 'conference_meeting/lobby.html',{'user_name':user_name})

@login_required
def room(request):
    print("🚀 Room view is being called!")
    user_name = request.user.username
    room_name = request.GET.get('room_password','DefaultRoom')
    return render(request, 'conference_meeting/room.html', {'room_name':room_name, 'user_name':user_name})

@login_required
def meetlist(request):
    return render(request,'conference_meeting/meetlist.html')

@login_required
def create_meeting(request):
    meeting_link = None  # Default value

    if request.method == "POST":
        meeting_name = request.POST.get("meeting_name")
        class_name = request.POST.get("class")
        password = request.POST.get("password")

        if meeting_name and class_name and password:
            salt = uuid.uuid4().hex
            meeting_id = generate_meeting_id(meeting_name, class_name, request.user.username)
            secret_key = generate_hmac_id(meeting_id, salt, password)

            meeting = Meeting.objects.create(
                meeting_id=meeting_id,
                salt=salt,
                secret_key=secret_key,
                host=request.user,
                class_name=class_name,
                is_active=True,
            )
            meeting_link = request.build_absolute_uri(f"/conference_meeting/{meeting.meeting_id}/")

    return render(request, "conference_meeting/create_meeting.html", {"meeting_link": meeting_link})

@csrf_exempt
def upload_recording(request):
    print(" upload_recording view HIT")
    print(" Method:", request.method)
    print(" FILES:", request.FILES)
    print(" POST:", request.POST)
    if request.method == 'POST' and request.FILES.get('recording'):
        recording = request.FILES['recording']
        meeting_id = request.POST.get('meeting_id')
        user_id = request.POST.get('recorded_by')

        print(" Parsed meeting_id:", meeting_id)
        print(" Parsed user_id:", user_id)

        if not meeting_id or not user_id:
            print(" Missing meeting_id or user_id")
            return JsonResponse({'error': 'Missing data'}, status=400)

        User = get_user_model()

        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)
            user = User.objects.get(id=user_id)
            print(" Found meeting and user")
        except (Meeting.DoesNotExist, User.DoesNotExist):
            print(" Meeting not found")
            print(" User not found")
            return JsonResponse({'error': 'Invalid meeting or user'}, status=404)

        save_dir = os.path.join(settings.MEDIA_ROOT, 'classrecordings')
        os.makedirs(save_dir, exist_ok=True)

        filename = f"recording_{meeting_id}_{now().strftime('%Y%m%d%H%M%S')}.webm"
        save_path = os.path.join(save_dir, filename)

        with open(save_path, 'wb+') as f:
            for chunk in recording.chunks():
                f.write(chunk)

        Recording.objects.create(
            meeting=meeting,
            recorded_by=user,
            file_path=os.path.join('classrecordings', filename)
        )
        print("Saving recording for", meeting, user)
        return JsonResponse({'message': 'Recording uploaded successfully.'})
    
    print(" Invalid request: Method or file missing")
    return JsonResponse({'error': 'Invalid request'}, status=400)
