from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware, now
from django.core.exceptions import PermissionDenied, ValidationError
import datetime
import logging
from django.utils.timezone import localtime
from django.db.models import Q
from .models import Meeting
from .forms import MeetingForm
from django.db.models.functions import Lower

logger = logging.getLogger(__name__)

@login_required
def create_meeting(request):
    """Create a new meeting with validation and scheduling."""
    prefilled_date = request.GET.get('date', None)

    if request.method == "POST":
        form = MeetingForm(request.POST, user=request.user)  # Pass user to filter institution

        if form.is_valid():
            try:
                meeting = form.save(commit=False)
                meeting.host = request.user

                # 🔹 Ensure all participants are from the same institution
                for participant in form.cleaned_data['participants']:
                    if participant.institution != request.user.institution:
                        return JsonResponse({"success": False, "error": "All participants must be from your institution."}, status=400)

                scheduled_time_str = request.POST.get('scheduled_time')
                end_time_str = request.POST.get('end_time')

                if not scheduled_time_str or not end_time_str:
                    return JsonResponse({"success": False, "error": "Scheduled time and End time are required."}, status=400)

                meeting.scheduled_time = make_aware(datetime.datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M'))
                meeting.end_time = make_aware(datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M'))

                if meeting.scheduled_time <= now():
                    return JsonResponse({"success": False, "error": "Meeting time must be in the future."}, status=400)

                if meeting.end_time <= meeting.scheduled_time:
                    return JsonResponse({"success": False, "error": "End time must be after the scheduled time."}, status=400)

                meeting.save()
                form.save_m2m()  # Save many-to-many relationships

                return JsonResponse({
                    "success": True,
                    "meeting_id": meeting.id,
                    "title": meeting.title,
                    "scheduled_time": meeting.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": meeting.end_time.strftime("%Y-%m-%d %H:%M"),
                    "redirect_url":reverse("conference_meeting:create_meeting")
                })

            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                return JsonResponse({"success": False, "error": str(e)}, status=400)

            except Exception as e:
                logger.error(f"Error creating meeting: {e}")
                return JsonResponse({"success": False, "error": "An unexpected error occurred."}, status=500)

        else:
            return JsonResponse({"success": False, "error": form.errors}, status=400)

    else:
        form = MeetingForm(initial={'scheduled_time': prefilled_date}, user=request.user)  # Pass user

    return render(request, 'meeting_scheduler/create_meeting.html', {'form': form})

@login_required
def meeting_detail(request, meeting_id):
    """View meeting details."""
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Restrict access to the same institution
    if meeting.host.institution != request.user.institution:
        raise PermissionDenied("You do not have permission to view this meeting.")

    return render(request, "meeting_scheduler/meeting_detail.html", {"meeting": meeting})
    
@login_required
def get_meetings(request):
    """Retrieve meetings with filtering and searching (restricted by institution)."""
    user = request.user
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    #  Filter meetings based on user participation AND institution
    meetings = Meeting.objects.filter(
        (Q(host=user) | Q(participants=user)) & Q(host__institution=user.institution)
    ).distinct()

    # Apply search filters
    if query:
        meetings = meetings.filter(Q(title__icontains=query) | Q(host__username__icontains=query))

    if status:
        meetings = meetings.filter(status=status)

    # Sorting logic
    sorting_options = {
        "scheduled_time_asc": "scheduled_time",
        "scheduled_time_desc": "-scheduled_time",
        "title_asc": "title",
        "title_desc": "-title",
        "host_asc": "host__username",
        "host_desc": "-host__username",
    }

    if sort_by in sorting_options:
        meetings = meetings.order_by(sorting_options[sort_by])

    # Convert meetings to JSON format
    events = [
        {
            "id": meeting.id,
            "title": meeting.title,
            "host": meeting.host.username,
            #"scheduled_time": meeting.scheduled_time.strftime("%Y-%m-%d %H:%M"),
            #"end_time": meeting.end_time.strftime("%Y-%m-%d %H:%M") if meeting.end_time else "N/A",
            
            "scheduled_time": localtime(meeting.scheduled_time).strftime("%B %d, %Y %I:%M %p"),
            "end_time": localtime(meeting.end_time).strftime("%B %d, %Y %I:%M %p") if meeting.end_time else "N/A",
            "status": meeting.status,
            "detail_url": reverse("meeting_scheduler:meeting_detail", args=[meeting.id]),
            "edit_url": reverse("meeting_scheduler:edit_meeting", args=[meeting.id]) if request.user == meeting.host else None,
            "delete_url": reverse("meeting_scheduler:delete_meeting", args=[meeting.id]) if request.user == meeting.host else None,
            "cancel_url": reverse("meeting_scheduler:cancel_meeting", args=[meeting.id]) if request.user == meeting.host and meeting.status != "Canceled" else None,
        }
        for meeting in meetings
    ]

    return JsonResponse(events, safe=False)

@login_required
def edit_meeting(request, meeting_id):
    """Edit a meeting (only the host from the same institution can edit)."""
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Ensure only the host can edit
    if request.user != meeting.host:
        return JsonResponse({"success": False, "error": "You do not have permission to edit this meeting."}, status=403)

    #Ensure meeting belongs to the same institution
    if meeting.host.institution != request.user.institution:
        return JsonResponse({"success": False, "error": "You cannot edit a meeting from another institution."}, status=403)

    # Define form before checking the request method
    form = MeetingForm(instance=meeting, user=request.user)

    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting, user=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})  # Return JSON response
        else:
            return JsonResponse({"success": False, "error": form.errors}, status=400)

    return render(request, 'meeting_scheduler/edit_meeting.html', {'form': form, 'meeting': meeting})

@login_required
def delete_meeting(request, meeting_id):
    """Delete a meeting (only the host from the same institution can delete)."""
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Ensure only the host can delete
    if request.user != meeting.host:
        raise PermissionDenied("You do not have permission to delete this meeting.")

    # Ensure the meeting belongs to the same institution
    if meeting.host.institution != request.user.institution:
        raise PermissionDenied("You cannot delete a meeting from another institution.")

    meeting.delete()
    return redirect('meeting_scheduler:all_meetings')


@login_required
def cancel_meeting(request, meeting_id):
    """Cancel a meeting (only the host from the same institution can cancel)."""
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Ensure only the host can cancel
    if request.user != meeting.host:
        raise PermissionDenied("You do not have permission to cancel this meeting.")

    # Ensure the meeting belongs to the same institution
    if meeting.host.institution != request.user.institution:
        raise PermissionDenied("You cannot cancel a meeting from another institution.")

    meeting.status = 'Canceled'
    meeting.save()
    return redirect('meeting_scheduler:meeting_detail', meeting_id=meeting.id)

@login_required
def all_meetings(request):
    """List all meetings with search and filtering (restricted by institution)."""
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    user = request.user

    # Superuser can see all meetings, but regular users are restricted by institution
    if user.is_superuser:
        meetings = Meeting.objects.all()
    else:
        meetings = Meeting.objects.filter(
            (Q(host=user) | Q(participants=user)) & Q(host__institution=user.institution)
        ).distinct()

    if search_query:
        meetings = meetings.filter(Q(title__icontains=search_query) | Q(host__username__icontains=search_query))

    if status_filter:
        meetings = meetings.filter(status=status_filter)

    paginator = Paginator(meetings.order_by('-scheduled_time'), 10)
    page_number = request.GET.get('page')
    meetings_page = paginator.get_page(page_number)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        meeting_data = [
            {
                "id": m.id,
                "title": m.title,
                "scheduled_time": m.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                "status": m.status
            }
            for m in meetings_page
        ]
        return JsonResponse({"meetings": meeting_data})

    return render(request, "meeting_scheduler/all_meetings.html", {"meetings": meetings_page})


@login_required
def search_meetings(request):
    """Search for meetings based on query and status (restricted by institution)."""
    query = request.GET.get("q", "").strip()
    filter_status = request.GET.get("status", "").strip()
    user = request.user

    meetings = Meeting.objects.filter(
        (Q(host=user) | Q(participants=user)) & Q(host__institution=user.institution)
    ).distinct()

    if query:
        meetings = meetings.filter(Q(title__icontains=query) | Q(host__username__icontains=query))

    if filter_status:
        meetings = meetings.filter(status=filter_status)

    return render(request, "meeting_scheduler/all_meetings.html", {"meetings": meetings})

@login_required
def update_meeting_status(request):
    """Update meeting statuses dynamically via API (restricted by institution)."""
    current_time = now()
    updated_meetings = []

    # Restrict meetings to the user's institution
    meetings = Meeting.objects.filter(host__institution=request.user.institution).exclude(status="Canceled")

    for meeting in meetings:
        old_status = meeting.status
        meeting.update_status()  

        if meeting.status != old_status:  
            updated_meetings.append({
                "id": meeting.id,
                "status": meeting.status,
            })

    return JsonResponse({"updated_meetings": updated_meetings})


@login_required
def get_meeting_status(request):
    """Fetch meeting status (restricted by institution)."""
    meeting_id = request.GET.get("id")
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Ensure user can only fetch status for meetings within their institution
    if meeting.host.institution != request.user.institution:
        return JsonResponse({"error": "You do not have permission to access this meeting."}, status=403)

    return JsonResponse({"status": meeting.status})