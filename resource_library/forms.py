from django import forms
from .models import Resource, Category
from classroom.models import Classroom
from django.db import models

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'file', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ResourceForm, self).__init__(*args, **kwargs)

        if user:
            # Get classroom titles taught by this instructor
            classroom_titles = Classroom.objects.filter(instructor=user).values_list('title', flat=True)

            if user.role == "Instructor":
                self.fields['category'].queryset = Category.objects.filter(
                    models.Q(name__in=classroom_titles) | models.Q(owner=user)
                )

            elif user.role == "Student":
                self.fields['category'].queryset = Category.objects.filter(owner=user)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
