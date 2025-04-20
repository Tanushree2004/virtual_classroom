# forms.py
from django import forms
from .models import Discussion, Comment, Category

from django import forms
from .models import Discussion, Comment, Category

class DiscussionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # get the user
        super().__init__(*args, **kwargs)

        # Filter categories if user is not instructor
        qs = Category.objects.all()
        if user and user.role != 'Instructor':
            qs = qs.exclude(slug='announcements')

        self.fields['category'].queryset = qs
        self.fields['category'].empty_label = "Select Category"

        # Optional: add visual hint
        for cat in qs:
            label = f"{cat.name} (Instructors only)" if cat.slug == "announcements" else cat.name
            self.fields['category'].choices = [(c.id, c.name) for c in qs]

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Will be replaced in __init__
        required=False,
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
