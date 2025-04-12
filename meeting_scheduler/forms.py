from django import forms
from .models import Meeting
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'scheduled_time', 'end_time', 'meeting_link', 'participants']
        
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user argument
        super().__init__(*args, **kwargs)

        self.fields['scheduled_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

        if user:
            # 🔹 Filter participants by institution
            self.fields['participants'].queryset = User.objects.filter(institution=user.institution, role="Student")
