from django.db import models
from django.utils import timezone
from dashboard.models import CustomUser 


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

class Discussion(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True,blank=True, related_name='discussions')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='discussions', null=True)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    
    @property
    def vote_score(self):
        return self.upvotes - self.downvotes

    def __str__(self):
        return self.title
        
# Add this new model
"""class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments',null =True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.discussion.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None
"""
class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments', null=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    def __str__(self):
        return f"Comment by {self.author.username if self.author else 'Anonymous'} on {self.discussion.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None
