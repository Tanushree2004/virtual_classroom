from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from rapidfuzz import process, fuzz  # Import RapidFuzz functions
from deep_translator import GoogleTranslator  # For language translation
from langdetect import detect  # For detecting the language of the question

# Predefined questions and responses for static answers
PREDEFINED_FAQ = {
    "how to submit an assignment": "To submit an assignment, navigate to the 'Assignments' section, select the assignment you want to complete, and upload your work.",
    "how to upload resources": "To upload resources, go to the 'Resource Library', click on the 'Upload Resource' button, choose your file, and then submit.",
    "how to edit my profile": "To edit your profile, click on your username or profile picture, select 'Edit Profile', update your information, and click 'Save'.",
    "how to delete a resource": "To delete a resource, open the 'Resource Library', find the resource you want to remove, and click on the delete icon (trash can) next to it.",
    "how to schedule a meet": "To schedule a meeting, go to the 'Meetings' section, click on 'Schedule a Meet', choose your desired date and time, and then confirm the meeting.",
    "how to join a class": "To join a class, navigate to the 'Classes' area, enter the class code provided by your instructor in the 'Join Class' section, and click 'Join'.",
    "who are you": "I am the LMS Helpbot, your virtual assistant designed to help you navigate the platform with ease.",
    "what is the purpose of a lms helpbot": "The purpose of the LMS Helpbot is to provide quick, pre-defined guidance on how to use various features of the platform—such as submitting assignments, uploading resources, and joining classes—so you can get the help you need when you need it.",
    "how to post a discussion": "To post a discussion, go to the 'Discussions' section, click on 'New Discussion', enter your message, and then click 'Post'."
}

def helpbot_home(request):
    """Display the helpbot interface."""
    return render(request, 'helpbot/home.html')

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
            detected_lang = detect(raw_question)
        except Exception:
            detected_lang = "en"  # Fallback to English if detection fails

        # Step 2: If detected language is not English, translate the question to English.
        if detected_lang != "en":
            translated_question = GoogleTranslator(source='auto', target='en').translate(raw_question)
        else:
            translated_question = raw_question

        # Normalize the question to lowercase for matching.
        translated_question_lower = translated_question.lower()

        response_text = None

        # Special handling for current date and time query.
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

        # Step 3: If the user’s original question was not in English, translate the response back.
        if detected_lang != "en":
            response_text = GoogleTranslator(source='en', target=detected_lang).translate(response_text)

        return JsonResponse({'response': response_text})
    
    return JsonResponse({'response': 'Invalid request method.'}, status=400)
def launcher_page(request):
    """Display the launcher page with the helpbot icon."""
    return render(request, 'helpbot/launcher.html')