from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from rapidfuzz import process, fuzz  # Import RapidFuzz functions
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from dashboard.models import UserPreference

# Predefined questions and responses for static answers
PREDEFINED_FAQ = {
    "how to submit an assignment": "To submit an assignment, navigate to the 'Assignments' section, select the assignment you want to complete, and upload your work.",
    "how to upload resources": "To upload resources, go to the 'Resource Library', create a new folder by clicking on  “add folder” for that resource if the required folder doesn’t already exist,click on the 'Upload Resource' button, choose your file, select category and then submit.",
    "how to edit my profile": "To edit your profile, Go to my Account, edit your user details or profile picture, select 'Edit Profile', update your information, and click 'Save'.",
    "how to delete a resource": "To delete a resource, open the 'Resource Library', find the resource you want to remove in its respective folder, and click on the delete icon  next to it, confirm delete and it will be deleted",
    "how to schedule a meet": "For admins or instructors, to schedule a meeting, go to the 'Meetings' section, click on 'Schedule a Meet', choose your desired date, time,title and then confirm the meeting. Feature not applicable for students",
    "how to join a scheduled meet": "Navigate to the ‘Meeting Scheduler’ tab, go to ‘View all meetings’ , click on the meeting link you want to join, enter credentials and join stream",
    "how to join a class": "If you are a student , reach out to your admin or instructor to get added to the particular class",
    "how to start a virtual class": "If you are an instructor or admin, navigate to classroom tab, click on the ‘Create Classroom’ button and you will be able to do it. Feature not applicable for students",
    "how to use the whiteboard": " Navigate to the ‘Others’ tab, select the ‘Whiteboard’ tab on the dashboard, start new whiteboard or revisit old one, give name to new whiteboard and happy doodling !!",
    "how to share my screen": "Click on the 'Share Screen' icon during a live meeting, choose the window or tab you want to share, and confirm. Make sure screen-sharing permissions are granted.",
    "how to record a session": "Toggle the 'Record' button after joining stream.",
    "how to access recorded lectures": "The class recordings will be available in your system automatically downloaded once the stop recording button is clicked ",
    "how to chat with classmates": "Open the 'Classroom’ tab, each class with a chatroom button will be visible, click the chatroom button of the classroom you want to chat in, you will be able to join",
    "how to post a discussion": "To post a discussion, go to the 'Discussion Forum' tab on Dashboard , click on 'New Discussion', enter your discussion topic title, write up, author name and then click 'Post'.",
    "who are you": "I am the LMS Helpbot, your virtual assistant designed to help you navigate the platform with ease.",
    "what is the purpose of a lms helpbot": "The purpose of the LMS Helpbot is to provide quick, guidance on how to use various features of the platform—such as submitting assignments, uploading resources, and joining classes—so you can get the help you need when you need it instead of awaiting external support",
    "how to access 3D models": "Navigate to ‘3D Models’ tab on dashboard, for Instructor : there will be a drop down to select whether you want to view or upload -> click on upload, fill the form and click upload ro successfully upload a model. For Student, you can  view the models on the ‘3D models’ tab itself",
    "How to use flashcards": "Navigate to ‘Others’ tab, click on ‘Flashcard’, upload the pdf or document you want flashcards on, click on ‘Generate Flashcards’, in a while flashcards will be displayed successfully on screen which you can shuffle between using keyboard right and left arrow keys",
    "Hello": "Hii, How can I help you today?",
    "Hi": "Hello, How can I help you today?",
    "Good morning": "Good Morning, How can I help you today?",
    "Good afternoon" : "Good Afternoon, How can I help you today?",
    "Good evening" : "Good Evening, How can I help you today?",
    "Good night" : "Good Night",
    "how to change font and theme": "Navigate to ‘Settings’ and the options will be available there",
    "how to logout": "Navigate to logout tab on dashboard",
    "How to view scheduled meetings": "You can view all scheduled meetings on the ‘Calendar ‘ Tab and also in the ‘View all Meetings’ section table of the ‘Meeting Scheduler’ tab",
    "how to create exam": "Navigate to ‘Exams’ tab, click on ‘create new Exam’, complete follow up steps to successfully create the exam",
    "how to give exam": "Navigate to ‘Exams’ tab, click on ‘Start exam’ link, you will be redirected to a full screen mode , ‘BE CAREFUL TO NOT CLICK ESC OR ANY OTHER KEY. IF YOU DO SO, YOUR EXAM WILL BE AUTOMATICALLY SUBMITTED BEFORE TIME ENDS AND YOU WILL BE OUT OF EXAM MODE",
    "how to access resources": "Navigate to ‘Resources’ tab, you will find the resource library section where you can find all resources and organize them as per your requirements",
    "how to create assignment": "Navigate to ‘Assignment’ tab, click on ‘Create your assignment’, follow up steps",
    "how to view assignment submissions": "Navigate to ‘Assignment’ tab, click on ‘View Assignments’, add remarks and save",
    "how to view submissions": "Navigate to ‘Assignment’ tab, click on ‘View Assignments’, add remarks and save",
}

def helpbot_home(request):
    if request.user.is_authenticated:
        preference, created = UserPreference.objects.get_or_create(user=request.user)
        bot_name = preference.helpbot_name  # Adjust according to your field
    else:
        bot_name = "HelpBot"
    return render(request, 'helpbot/home.html', {'bot_name': bot_name})

def get_help_response(request):
    """
    Return a response based on the user's question.
    The helpbot now supports only English and responds to predefined questions.
    """
    if request.method == "POST":
        # Get the user's question from the POST data.
        raw_question = request.POST.get('question', '').strip()
        question_lower = raw_question.lower()

        response_text = None

        # Special handling for the current date and time query.
        if "what is the date and time" in question_lower:
            current_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response_text = f"The current date and time is: {current_dt}"
        else:
            # Determine the best matching predefined question using RapidFuzz.
            best_match = process.extractOne(
                question_lower,
                PREDEFINED_FAQ.keys(),
                scorer=fuzz.token_set_ratio
            )
            if best_match and best_match[1] >= 70:
                response_text = PREDEFINED_FAQ[best_match[0]]
            else:
                response_text = "Sorry, I do not have an answer for that question."

        return JsonResponse({'response': response_text})
    
    return JsonResponse({'response': 'Invalid request method.'}, status=400)

@login_required
@require_POST
def update_helpbot_name(request):
    new_name = request.POST.get('new_name', '').strip()
    if new_name:
        preference = request.user.userpreference
        preference.helpbot_name = new_name
        preference.save()
        return JsonResponse({'status': 'success', 'new_name': new_name})
    return JsonResponse({'status': 'error', 'message': 'Invalid name'}, status=400)
