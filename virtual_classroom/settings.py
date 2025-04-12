
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
GROQ_API_KEY = "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"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
SECRET_KEY = 'django-insecure-pj!^xdk8d7!8#29hz@i&l$zu2itim9g6u(@c+_emmj!s3me2pa'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'classroom',
    'meeting_scheduler',
    'calendarapp',
    'chatroom',
    'channels',
    'threeDmodels',
    'plagiarism_checker',
    'whiteboard',
    'exam',
    'assignments_app',
    'flashcards',
    'conference_meeting',
    'discussions',
    'helpbot',

    'django_extensions',
    'rest_framework',
    #'channels',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
ROOT_URLCONF = 'virtual_classroom.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.user_preferences',
            ],
        },
    },
]
WSGI_APPLICATION = 'virtual_classroom.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'dashboard.CustomUser'
STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "dashboard/static",
    BASE_DIR / "classroom/static",
    BASE_DIR / "calendarapp/static",
    BASE_DIR / "chatroom/static",
    BASE_DIR / "meeting_scheduler/static",
    BASE_DIR / "threeDmodels/static",
    BASE_DIR / "assignments_app/static",
    BASE_DIR / "flashcards/static",
    BASE_DIR / "exam/static",
    BASE_DIR / "whiteboard/static",
]
LOGIN_URL = '/login/' 
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'classroom_resources')
ASGI_APPLICATION = "virtual_classroom.asgi.application"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90  
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
DATABASE_ROUTERS = ['virtual_classroom.routers.MultiTenantRouter']
MIDDLEWARE.append('virtual_classroom.middleware.TenantMiddleware')

load_dotenv()
GOOGLE_NEWS_API_KEY = os.getenv("GOOGLE_NEWS_API_KEY")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
CSP_CONNECT_SRC = ("'self'", "wss://127.0.0.1:8000")
