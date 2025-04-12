from django.shortcuts import render, get_object_or_404
from meeting_scheduler.models import Meeting
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def calendar_view(request):
    return render(request, 'calendarapp/calendar.html')
@login_required
def get_meetings(request):
    current_user = request.user
    meetings = Meeting.objects.filter(status__in=['Upcoming', 'Ongoing']).filter(host=current_user) | Meeting.objects.filter(participants=current_user)

    event_list = []
    for meeting in meetings.distinct(): 
        event_list.append({
            "id": meeting.id,
            "title": meeting.title,  
            "start": meeting.scheduled_time.isoformat(),
            "end": meeting.end_time.isoformat(),
            "url": reverse('meeting_scheduler:meeting_detail', args=[meeting.id]),  
            "host_id": meeting.host.id  
        })
    return JsonResponse(event_list, safe=False)
@csrf_exempt
@login_required
def update_meeting_date(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        new_date = request.POST.get('new_date')
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user != meeting.host:
            return JsonResponse({'error': 'You are not the host of this meeting!'}, status=403)
        new_scheduled_time = meeting.scheduled_time.replace(
            year=int(new_date.split('-')[0]),
            month=int(new_date.split('-')[1]),
            day=int(new_date.split('-')[2])
        )
        new_end_time = meeting.end_time.replace(
            year=int(new_date.split('-')[0]),
            month=int(new_date.split('-')[1]),
            day=int(new_date.split('-')[2])
        )
        meeting.scheduled_time = new_scheduled_time
        meeting.end_time = new_end_time
        meeting.save()
        return JsonResponse({'message': 'Meeting updated successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)