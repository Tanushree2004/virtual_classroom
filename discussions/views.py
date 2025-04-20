from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Discussion, Vote, Comment
from .forms import DiscussionForm, CommentForm
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
import json

@login_required
def discussion_list(request):
    main_categories = Category.objects.filter(parent__isnull=True)
    query = request.GET.get('q', '')
    if query:
        all_discussions = Discussion.objects.filter(
            Q(title__icontains=query) | Q(author__username__icontains=query)
        ).order_by('-created_at')
    else:
        all_discussions = Discussion.objects.all().order_by('-created_at')

    paginator = Paginator(all_discussions, 10)
    page_number = request.GET.get('page')
    latest_discussions = paginator.get_page(page_number)

    context = {
        'main_categories': main_categories,
        'latest_discussions': latest_discussions,
        'query': query,
    }
    return render(request, 'discussions/discussion_list.html', context)


@login_required
def category_discussions(request, slug):
    category = get_object_or_404(Category, slug=slug)
    discussions = Discussion.objects.filter(category=category).order_by('-created_at')

    is_announcement = category.slug == "announcements"
    can_post = not is_announcement or request.user.role == "Instructor"

    return render(request, 'discussions/category_discussions.html', {
        'category': category,
        'discussions': discussions,
        'can_post': can_post,
        'is_announcement': is_announcement,
    })



@login_required
def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.cleaned_data.get('category')

            # Restrict posting in announcements to instructors only
            if category and category.slug == 'announcements' and request.user.role != 'Instructor':
                return HttpResponseForbidden("Only instructors can post in the Announcements category.")

            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            return redirect('discussions:discussion_list')
    else:
        form = DiscussionForm(user=request.user)

    return render(request, 'discussions/create_discussion.html', {'form': form})



@login_required
def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = discussion.comments.filter(parent__isnull=True).order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.author = request.user

            reply_to = form.cleaned_data.get('reply_to')
            if reply_to:
                parent_comment = Comment.objects.get(id=reply_to)
                comment.parent = parent_comment

            comment.save()

            return JsonResponse({
                'success': True,
                'id': comment.id,
                'author_name': request.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime("%b %d, %Y %I:%M %p"),
                'is_reply': comment.is_reply,
                'parent_id': comment.parent.id if comment.parent else None
            })

    return render(request, 'discussions/discussion_detail.html', {
        'discussion': discussion,
        'comments': comments,
        'comment_form': CommentForm()
    })


@login_required
@require_POST
def vote_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body)
        vote_type = data.get('vote_type')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    if vote_type not in ['upvote', 'downvote']:
        return JsonResponse({'success': False, 'error': 'Invalid vote type.'}, status=400)

    user = request.user
    existing_vote = Vote.objects.filter(user=user, discussion=discussion).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        Vote.objects.create(user=user, discussion=discussion, vote_type=vote_type)

    upvotes = Vote.objects.filter(discussion=discussion, vote_type='upvote').count()
    downvotes = Vote.objects.filter(discussion=discussion, vote_type='downvote').count()

    discussion.upvotes = upvotes
    discussion.downvotes = downvotes
    discussion.save()

    return JsonResponse({
        'success': True,
        'vote_score': discussion.vote_score,
        'upvotes': upvotes,
        'downvotes': downvotes
    })


@login_required
@require_POST
def add_category(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        category_name = request.POST.get('category_name', '').strip()
        if category_name:
            slug = slugify(category_name)
            if Category.objects.filter(slug=slug).exists():
                return JsonResponse({'success': False, 'error': 'Category already exists.'})
            category = Category.objects.create(name=category_name, slug=slug)
            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            })
        else:
            return JsonResponse({'success': False, 'error': 'No category name provided.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})
