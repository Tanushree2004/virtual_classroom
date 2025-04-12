from django import forms
from .models import Assignment
from classroom.models import Classroom

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['name','description','group','deadline']

    def __init__(self, *args, **kwargs):
        instructor = kwargs.pop('instructor', None)  # ✅ get instructor from kwargs
        super().__init__(*args, **kwargs)

        if instructor:
            # ✅ Limit group choices to classrooms this instructor teaches
            self.fields['group'].queryset = Classroom.objects.filter(instructor=instructor)