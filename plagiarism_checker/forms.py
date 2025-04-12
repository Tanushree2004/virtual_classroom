from django import forms
from .models import PlagiarismCheck

class PlagiarismCheckForm(forms.ModelForm):
    class Meta:
        model = PlagiarismCheck
        fields = ['file1', 'file2']
