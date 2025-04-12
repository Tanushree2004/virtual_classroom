from django import forms
from .models import ThreeDModel

class ThreeDModelForm(forms.ModelForm):
    class Meta:
        model = ThreeDModel
        fields = ['name', 'model_file']
