import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ======================================
#  RUTA BASE
# ======================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
SECRET_KEY = 'django-insecure-gr+ag+9gblo6w%x$ow+63$gxjlvb9o^zffb)s*4stlpoj+j(c0'
DEBUG = True
ALLOWED_HOSTS = ["*"]


# ======================================
# APPS INSTALADAS
# ======================================
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.staticfiles',

    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',

    'catalog.apps.CatalogConfig',
    'happyhuapi.apps.HappyhuapiConfig',
]


# ======================================
# CLOUDINARY
# ======================================
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'doq7wqfcw',
    'API_KEY': '483729672631914',
    'API_SECRET': 'CqYTgW6F9bYYqPBOyzunJDC6gxk',
    'PREFIX': 'catalog',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ======================================
# MIDDLEWARE
# ======================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ======================================
# URL RAÍZ
# ======================================
ROOT_URLCONF = 'happyhuapi.urls'


# ======================================
# TEMPLATES
# ======================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================================
# WSGI
# ======================================
WSGI_APPLICATION = 'happyhuapi.wsgi.application'


# ======================================
# BASE DE DATOS 
# ======================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    }
}



# ======================================
# VALIDADORES DE CONTRASEÑA
# ======================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ======================================
# LOCALIZACIÓN / HORARIO
# ======================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# ======================================
# CONFIGURACIÓN PARA TESTS
# ======================================
if 'test' in sys.argv or 'pytest' in sys.argv:
    print(" Modo de test ultra rápido activado")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()

    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = Path(BASE_DIR) / "test_media"
    LOGGING = {}


# ======================================
# ARCHIVOS ESTÁTICOS
# ======================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================
# LOGIN / LOGOUT 
# ======================================
LOGIN_URL = "/login/"               # URL real del login
LOGIN_REDIRECT_URL = "/"            # Después de loguear
LOGOUT_REDIRECT_URL = "/"           # Después de salir


# ======================================
# CONFIGURACIÓN DE EMAIL (GMAIL)
# ======================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "happyhuapi4@gmail.com"
EMAIL_HOST_PASSWORD = "qjxg mxhl dcvx nmug"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ======================================
# CONFIG WEBPAY PRUEBA
# ======================================
BASE_URL = "http://127.0.0.1:8000"
WEBPAY_COMMERCE_CODE = "597055555532"
WEBPAY_API_KEY = "579B532AFBAFDAD6DFA1C3F4FBAF16E0"
