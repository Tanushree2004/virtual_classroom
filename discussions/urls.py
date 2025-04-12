from django.urls import path
from . import views

app_name = 'discussions'  # Add this for namespace

urlpatterns = [
    # Homepage - shows latest discussions
    path('', views.discussion_list, name='discussion_list'),
    
    # Category view - shows discussions in a specific category
    path('category/<slug:slug>/', views.category_discussions, name='category_discussions'),
    
    # Create new discussion
    path('new/', views.create_discussion, name='create_discussion'),
    
    # Discussion detail view - shows full content
    path('discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    
    # Add to urls.py
   path('discussions/<int:pk>/vote/', views.vote_discussion, name='vote_discussion'),
    # Alternative simple URL pattern (optional)
    #path('<int:pk>/', views.discussion_detail, name='discussion_detail_alt'),
   path('add_category/', views.add_category, name='add_category'),
    
]