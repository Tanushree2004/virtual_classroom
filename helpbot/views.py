from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from rapidfuzz import process, fuzz  # Import RapidFuzz functions
from deep_translator import GoogleTranslator  # For language translation
from langdetect import detect  # For detecting the language of the question
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from dashboard.models import UserPreference
from functools import lru_cache

# Predefined questions and responses for static answers
PREDEFINED_FAQ = {
    "how to submit an assignment": "To submit an assignment, navigate to the 'Assignments' section, select the assignment you want to complete, and upload your work.",
    "how to upload resources": "To upload resources, go to the 'Resource Library', click on the 'Upload Resource' button, choose your file, and then submit.",
    "how to edit my profile": "To edit your profile, click on your username or profile picture, select 'Edit Profile', update your information, and click 'Save'.",
    "how to delete a resource": "To delete a resource, open the 'Resource Library', find the resource you want to remove, and click on the delete icon (trash can) next to it.",
    "how to schedule a meet": "To schedule a meeting, go to the 'Meetings' section, click on 'Schedule a Meet', choose your desired date and time, and then confirm the meeting.",
    "how to join a class": "To join a class, navigate to the 'Classes' area, enter the class code provided by your instructor in the 'Join Class' section, and click 'Join'.",
    "how to take attendance": "To take attendance, go to the 'Attendance' module, select your class, choose the session, and mark students as present, absent, or late.",
    "how to start a virtual class": "To start a virtual class, go to the 'Meetings' section, click 'Start Now' next to the scheduled meeting or create a new one and launch it immediately.",
    "how to join a virtual classroom": "Click on the meeting link shared by your instructor or navigate to 'Upcoming Meetings' and click 'Join'. Make sure your mic and camera permissions are enabled.",
    "how to raise a hand in class": "During a live session, click the 'Raise Hand' button on the control bar to notify your instructor you have a question.",
    "how to use the whiteboard": "If your instructor enables the whiteboard, you can access it during a session by clicking the 'Whiteboard' icon in the toolbar and collaborate in real-time.",
    "how to share my screen": "Click on the 'Share Screen' icon during a live class, choose the window or tab you want to share, and confirm. Make sure screen-sharing permissions are granted.",
    "how to record a session": "If you're the instructor, toggle the 'Record' button before starting the class. Students should check with their instructor for access to recordings.",
    "how to access recorded lectures": "Go to the 'Class Recordings' section from your dashboard, choose the subject, and select the date to watch or download the session.",
    "how to chat with classmates": "Open the 'Class Chat' tab during a session or visit the 'Discussions' section outside of class to start or join a conversation.",
    "how to post a discussion": "To post a discussion, go to the 'Discussions' section, click on 'New Discussion', enter your message, and then click 'Post'.",
    "how to use breakout rooms": "During a live class, your instructor can move participants into breakout rooms. You’ll automatically be placed in a small group and can rejoin the main session anytime.",
    "who are you": "I am the LMS Helpbot, your virtual assistant designed to help you navigate the platform with ease.",
    "what is the purpose of a lms helpbot": "The purpose of the LMS Helpbot is to provide quick, pre-defined guidance on how to use various features of the platform—such as submitting assignments, uploading resources, and joining classes—so you can get the help you need when you need it."
}

# Global translator instance for translating to English; reused across requests.
default_translator = GoogleTranslator(source='auto', target='en')

# Cache translation calls to avoid repeated heavy operations.
@lru_cache(maxsize=128)
def translate_text(text, source, target):
    return GoogleTranslator(source=source, target=target).translate(text)

def helpbot_home(request):
    if request.user.is_authenticated:
        preference, created = UserPreference.objects.get_or_create(user=request.user)
        bot_name = preference.helpbot_name  # Adjust according to your field (if not defined, you might set a default name)
    else:
        bot_name = "HelpBot"
    return render(request, 'helpbot/home.html', {'bot_name': bot_name})

def get_help_response(request):
    """
    Return a response based on the user's question while supporting multiple languages.
    The bot automatically translates non-English input to English for processing,
    and then translates the answer back to the original language.
    """
    if request.method == "POST":
        # Retrieve the raw question as provided by the user
        raw_question = request.POST.get('question', '').strip()

        # Step 1: Detect the language of the user question.
        try:
            if len(raw_question) <= 3:
                detected_lang = "en"
            else:
                detected_lang = detect(raw_question)
        except Exception:
            detected_lang = "en"

        # Step 2: Translate the question to English if the detected language is not English.
        if detected_lang != "en":
            translated_question = translate_text(raw_question, source='auto', target='en')
        else:
            translated_question = raw_question

        # Normalize the question to lowercase for matching.
        translated_question_lower = translated_question.lower()

        response_text = None

        # Special handling for date and time query.
        if "what is the date and time" in translated_question_lower:
            current_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response_text = f"The current date and time is: {current_dt}"
        else:
            # Use RapidFuzz to determine the best matching predefined question.
            best_match = process.extractOne(
                translated_question_lower,
                PREDEFINED_FAQ.keys(),
                scorer=fuzz.token_set_ratio
            )
            if best_match and best_match[1] >= 70:
                response_text = PREDEFINED_FAQ[best_match[0]]
            else:
                response_text = "Sorry, I do not have an answer for that question."

        # Step 3: If the original question was not in English, translate the response back.
        if detected_lang != "en":
            response_text = translate_text(response_text, source='en', target=detected_lang)

        return JsonResponse({'response': response_text})
    
    return JsonResponse({'response': 'Invalid request method.'}, status=400)

@login_required
@require_POST
def update_helpbot_name(request):
    new_name = request.POST.get('new_name', '').strip()
    if new_name:
        # Update the user's helpbot name in their preferences.
        preference = request.user.userpreference
        preference.helpbot_name = new_name
        preference.save()
        return JsonResponse({'status': 'success', 'new_name': new_name})
    return JsonResponse({'status': 'error', 'message': 'Invalid name'}, status=400)
