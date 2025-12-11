import os
import sys
from pathlib import Path


#  Ruta base 
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
SECRET_KEY = 'django-insecure-gr+ag+9gblo6w%x$ow+63$gxjlvb9o^zffb)s*4stlpoj+j(c0'
DEBUG = True
ALLOWED_HOSTS = []


# ======================================
# APPS INSTALADAS
# ======================================
INSTALLED_APPS = [
    'cloudinary_storage',   # debe ir antes del manejo de archivos
    'django.contrib.staticfiles',

    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'catalog.apps.CatalogConfig',   # Tu app de productos
    'happyhuapi.apps.HappyhuapiConfig',  # Tu app principal
]


# ======================================
# CLOUDINARY (IMÁGENES)
# ======================================
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
  'CLOUD_NAME': 'doq7wqfcw',
  'API_KEY': '483729672631914',
  'API_SECRET': 'CqYTgW6F9bYYqPBOyzunJDC6gxk',
  'PREFIX': 'catalog',   # donde se guardan las imágenes en Cloudinary
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


ROOT_URLCONF = 'happyhuapi.urls'


# ======================================
# TEMPLATES (AQUÍ ESTABA EL PROBLEMA)
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





WSGI_APPLICATION = 'happyhuapi.wsgi.application'


# ======================================
# BASE DE DATOS
# ======================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'WlUFbvlSnOXtXPYKBSyPGrkLpwoqqNMY',
        'HOST': 'yamanote.proxy.rlwy.net',
        'PORT': '55022',
    }
}


# ======================================
# AUTH
# ======================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ======================================
# LOCALIZACIÓN / HORA
# ======================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# ======================================
#  OPTIMIZACIÓN TOTAL PARA TESTS
# ======================================
if 'test' in sys.argv or 'pytest' in sys.argv:
    print(" Modo de test ultra rápido activado")

    #  Base de datos en memoria (instantánea)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

    #  Desactivar migraciones (carga inmediata)
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    MIGRATION_MODULES = DisableMigrations()

    #  Desactivar Cloudinary (usa almacenamiento local temporal)
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = Path(BASE_DIR) / "test_media"
    
    #  Desactivar logs o tareas innecesarias
    LOGGING = {}


# ======================================
# ARCHIVOS ESTÁTICOS
# ======================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "Reservas"
LOGOUT_REDIRECT_URL = "Inicio"

# CONFIGURACIÓN DE EMAIL (GMAIL)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "happyhuapi4@gmail.com"
EMAIL_HOST_PASSWORD = "qjxg mxhl dcvx nmug"
