# context_processors.py

from .models import UserPreference

def user_preferences(request):
    if request.user.is_authenticated:
        try:
            prefs = UserPreference.objects.get(user=request.user)
            return {
                'user_theme': prefs.theme,
                'user_font_size': prefs.font_size,
                'user_font_style': prefs.font_style,
                
            }
        except UserPreference.DoesNotExist:
            pass
    return {}
