# forms.py
from django import forms
from .models import Discussion, Comment, Category

class DiscussionForm(forms.ModelForm):
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select Category"
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'category']
        exclude = ['author', 'created_at', 'upvotes', 'downvotes']

class CommentForm(forms.ModelForm):
    '''author_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your name (optional)'})
    )'''
    reply_to = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Comment
        fields = ['content']


# seed_categories.py
# This script can be run to add initial categories to your database.
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_classroom.settings')
django.setup()

from discussions.models import Category

categories = ["announcements", "qna", "ideas/suggestions", "algorithms", "tests", "news"]

for cat in categories:
    # Use a capitalized name for display and create a slug by replacing spaces and slashes with hyphens.
    name = cat.capitalize()
    slug = cat.lower().replace(" ", "-").replace("/", "-")
    category, created = Category.objects.get_or_create(name=name, slug=slug)
    if created:
        print(f"Created category: {name}")
    else:
        print(f"Category already exists: {name}")
