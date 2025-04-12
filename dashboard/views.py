from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import CustomUser, UserPreference, Institution
from .forms import CustomUserForm, ProfileForm, UserPreferenceForm
from classroom.models import Classroom
from meeting_scheduler.models import Meeting
import requests
import os
import re

GOOGLE_NEWS_API_KEY = os.getenv("GOOGLE_NEWS_API_KEY")


def is_admin(user):
    return user.role == 'Admin'

def is_instructor(user):
    return user.role == 'Instructor'

def is_student(user):
    return user.role == 'Student'

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_role = request.user.role
    if user_role == 'Admin':
        return redirect('admin_dashboard')
    elif user_role == 'Instructor':
        return redirect('instructor_dashboard')
    else:
        return redirect('student_dashboard')

def fetch_research_papers(search_query):
    recommended_papers = []
    semantic_scholar_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={search_query}&limit=15&fields=title,authors,paperId,citationCount,url"
    response = requests.get(semantic_scholar_url)
    if response.status_code == 200:
        try:
            data = response.json().get("data", [])
            papers = sorted(data, key=lambda x: x.get("citationCount", 0), reverse=True)
            for paper in papers[:10]:
                recommended_papers.append({
                    "title": paper.get("title", "Unknown Title"),
                    "url": f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                    "authors": ", ".join([author["name"] for author in paper.get("authors", []) if "name" in author]),
                    "citations": paper.get("citationCount", 0)
                })
        except Exception as e:
            print(f"Error processing Semantic Scholar response: {e}")

    arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=10"
    response = requests.get(arxiv_url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                recommended_papers.append({
                    "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                    "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
                    "authors": ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")]),
                    "citations": "arXiv (No Citations Available)"
                })
        except Exception as e:
            print(f"Error processing arXiv response: {e}")
    return recommended_papers

def fetch_news_articles(search_query):
    recommended_articles = []
    google_news_url = f"https://newsapi.org/v2/everything?q={search_query}&language=en&sortBy=popularity&pageSize=15&apiKey={GOOGLE_NEWS_API_KEY}"
    response = requests.get(google_news_url)   
    if response.status_code == 200:
        try:
            articles = response.json().get("articles", [])
            for article in articles:
                recommended_articles.append({
                    "title": article.get("title", "No Title"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name", "Unknown Source"),
                    "published_at": article.get("publishedAt", "No Date")
                })
        except Exception as e:
            print(f"Error processing Google News response: {e}")
    return recommended_articles

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = CustomUser.objects.filter(institution=request.user.institution).count()
    active_users = CustomUser.objects.filter(institution=request.user.institution, is_active=True).count()
    inactive_users = CustomUser.objects.filter(institution=request.user.institution, is_active=False).count()
    total_classrooms = Classroom.objects.filter(instructor__institution=request.user.institution).count()
    total_instructors = Classroom.objects.filter(instructor__institution=request.user.institution).values('instructor').distinct().count()
    total_students = Classroom.objects.filter(students__institution=request.user.institution).values('students').distinct().count()
    upcoming_meetings = Meeting.objects.filter(
        scheduled_time__gte=timezone.now(),
        host__institution=request.user.institution 
    ).order_by('scheduled_time')[:5]
    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_classrooms': total_classrooms,
        'total_instructors': total_instructors,
        'total_students': total_students,
        'upcoming_meetings': upcoming_meetings,
    })

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    user = request.user
    classrooms = Classroom.objects.filter(instructor=user, instructor__institution=user.institution)
    upcoming_meetings = Meeting.objects.filter(
        scheduled_time__gte=timezone.now(),
        host=user,  
        host__institution=user.institution  
    ).order_by('scheduled_time')

    search_query = request.GET.get("search_query", "").strip()
    if not search_query:
        search_query = " ".join([f"{c.title} {c.description}" for c in classrooms])

    recommended_papers = fetch_research_papers(search_query)
    recommended_articles = fetch_news_articles(search_query)
    return render(request, 'instructor_dashboard.html', {
        'classrooms': classrooms,
        'recommended_papers': recommended_papers,
        'recommended_articles': recommended_articles,
        'search_query': search_query,
        'meetings': upcoming_meetings
    })


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    user = request.user
    classrooms = Classroom.objects.filter(students=user)
    upcoming_meetings = Meeting.objects.filter(
        scheduled_time__gte=timezone.now(),
        participants__id=user.id,  
        host__institution=user.institution
    ).order_by('scheduled_time')
    search_query = request.GET.get("search_query", "").strip()
    if not search_query:
        search_query = " ".join([f"{c.title} {c.description}" for c in classrooms])

    recommended_papers = fetch_research_papers(search_query)
    recommended_articles = fetch_news_articles(search_query)
    return render(request, 'student_dashboard.html', {
        'classrooms': classrooms,
        'recommended_papers': recommended_papers,
        'recommended_articles': recommended_articles,
        'search_query': search_query,
        'meetings': upcoming_meetings
    })

@login_required
def profile_view(request):
    user = request.user
    success = False  

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            success = True  
    else:
        form = ProfileForm(instance=user)

    return render(request, "dashboard/profile.html", {"form": form, "user": user, "success": success})

def user_list(request):
    users = CustomUser.objects.filter(institution=request.user.institution)  
    return render(request, 'user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '').lower()
            username = form.cleaned_data.get('username', '').strip()

            # ✅ Validate email format
            email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
            if not re.match(email_regex, email):
                messages.error(request, 'Invalid email format. Use only lowercase letters and allowed characters.')
                return render(request, 'add_user.html', {'form': form})

            # ✅ Check email uniqueness
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'add_user.html', {'form': form})

            # ✅ Check username uniqueness
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'add_user.html', {'form': form})

            # ✅ Save user
            user = form.save(commit=False)
            user.email = email
            user.username = username
            user.institution = request.user.institution
            user.password = make_password(form.cleaned_data['password1'])
            user.save()

            messages.success(request, 'User added successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error in form submission.')
    else:
        form = CustomUserForm()
    return render(request, 'add_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.institution != request.user.institution:
        messages.error(request, "You are not allowed to edit users from another institution.")
        return redirect('user_list')

    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        #form = CustomUserForm(request.POST or None)  # No hide_role — dropdown will show
        if form.is_valid():
            updated_user = form.save(commit=False)

            # ✅ Lowercase email and strip username
            email = form.cleaned_data.get('email', '').lower()
            username = form.cleaned_data.get('username', '').strip()

            # ✅ Validate email format
            email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
            if not re.match(email_regex, email):
                messages.error(request, 'Invalid email format. Use only lowercase letters and allowed characters.')
                return render(request, 'edit_user.html', {'form': form})

            # ✅ Check email uniqueness (excluding current user)
            if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'edit_user.html', {'form': form})

            # ✅ Check username uniqueness (excluding current user)
            if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'edit_user.html', {'form': form})

            updated_user.email = email
            updated_user.username = username

            # ✅ Role restriction: non-admins can't assign Admin role
            if request.user.role != "Admin" and updated_user.role == "Admin":
                messages.error(request, "You cannot assign an Admin role.")
                return redirect('edit_user', user_id=user.id)

            updated_user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error updating user.')
    else:
        form = CustomUserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.institution != request.user.institution:
        messages.error(request, "You are not allowed to delete users from another institution.")
        return redirect('user_list')
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('user_list')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            request.session.set_expiry(60 * 60 * 24 * 90 if request.POST.get('remember_me') else None)
            if user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'Instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('login')

def landing_page(request):
    return render(request, 'landing.html')

def about(request):
    return render(request, 'about.html')

@login_required
def user_settings(request):
    prefs, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            return redirect('dashboard_view')  # Or your homepage/dashboard route
    else:
        form = UserPreferenceForm(instance=prefs)

    return render(request, 'settings.html', {'form': form})


def admin_register_view(request):
    if request.method == 'POST':
        #form = CustomUserForm(request.POST)
        form = CustomUserForm(request.POST or None, hide_role=True)
        institution_name = request.POST.get('institution_name')

        if form.is_valid():
            # Check if institution already exists
            if Institution.objects.filter(name__iexact=institution_name).exists():
                institution = Institution.objects.get(name__iexact=institution_name)

                # Check if Admin already exists for this institution
                if CustomUser.objects.filter(role='Admin', institution=institution).exists():
                    messages.error(request, 'An Admin already exists for this institution.')
                    return render(request, 'register_admin.html', {'form': form})
            else:
                # Create new institution
                institution = Institution.objects.create(
                    name=institution_name,
                    database_name=institution_name.lower().replace(" ", "_")
                )

            # Register admin
            user = form.save(commit=False)
            user.role = 'Admin'
            user.institution = institution
            user.password = make_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Institution Admin registered successfully.')
            return redirect('login')
    else:
        form = CustomUserForm(hide_role=True)

    return render(request, 'register_admin.html', {'form': form})