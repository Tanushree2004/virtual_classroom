from django import forms
from django.contrib.auth.hashers import make_password
from .models import CustomUser,Institution, UserPreference

class CustomUserForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput, 
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, 
        label='Confirm Password'
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        hide_role = kwargs.pop('hide_role', False)
        super().__init__(*args, **kwargs)

        if hide_role:
            self.fields.pop('role')  # Removes the field from the form

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "profile_image",
            "session_year", "semester", "student_class", "course", "student_id",
            "faculty", "position"
        ]

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['theme', 'font_size', 'font_style']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'font_size': forms.Select(attrs={'class': 'form-control'}),
            'font_style': forms.Select(attrs={'class': 'form-control'}),
            
        }