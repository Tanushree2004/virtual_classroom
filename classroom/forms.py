from django import forms
from .models import Classroom, ClassroomResource
from django.contrib.auth import get_user_model

User = get_user_model()

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['title', 'description', 'instructor', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the current user from the view
        super().__init__(*args, **kwargs)

        if user:
            # Filter students by institution
            self.fields['students'].queryset = User.objects.filter(role="Student", institution=user.institution)

            if user.role == "Admin":
                # Admins can select from all instructors in their institution
                self.fields['instructor'].queryset = User.objects.filter(role="Instructor", institution=user.institution)

            elif user.role == "Instructor":
                # Instructors can only assign themselves and field is disabled
                self.fields['instructor'].queryset = User.objects.filter(id=user.id)
                self.fields['instructor'].initial = user
                self.fields['instructor'].disabled = True

class InviteStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role="Student"),
        label="Select Student"
    )

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution', None)  # Get institution from the view
        super().__init__(*args, **kwargs)

        if institution:
            # Filter students by institution
            self.fields['student'].queryset = User.objects.filter(role="Student", institution=institution)

class ClassroomResourceForm(forms.ModelForm):
    class Meta:
        model = ClassroomResource
        fields = ['title', 'resource_type', 'file', 'link']
