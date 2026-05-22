"""
Django settings for config project.
"""

from pathlib import Path
import os
import dj_database_url
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================
# CORE SETTINGS - ĐỌC TỪ FILE .ENV (KHÔNG HARDCODE!)
# ==============================================================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# ==============================================================
# APPLICATION DEFINITION
# ==============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'maps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise serve static files trên production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================
# DATABASE
# Ưu tiên DATABASE_URL (Render/Neon production), fallback về cấu hình local
# ==============================================================

DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production: Render hoặc Neon.tech (dùng PostGIS backend)
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            engine='django.contrib.gis.db.backends.postgis',
        )
    }
else:
    # Development local: đọc từ .env
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': config('DB_NAME', default='duangismoi'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }


# ==============================================================
# PASSWORD VALIDATION
# ==============================================================

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


# ==============================================================
# INTERNATIONALIZATION
# ==============================================================

LANGUAGE_CODE = 'vi'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True


# ==============================================================
# STATIC & MEDIA FILES
# ==============================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise: Nén và cache static files tự động
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================================================
# DEFAULT PRIMARY KEY
# ==============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================
# EMAIL CONFIGURATION (Gmail SMTP) - ĐỌC TỪ .ENV
# ==============================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Urban Manager <noreply@urbanmanager.com>')


# ==============================================================
# GEODJANGO - CẤU HÌNH GDAL/GEOS CHO CẢ WINDOWS LẪN LINUX
# ==============================================================

if os.name == 'nt':
    # ---- WINDOWS (Development) ----
    import glob
    gdal_candidates = glob.glob(r'C:\Program Files\PostgreSQL\*\bin\libgdal*.dll')
    geos_candidates = glob.glob(r'C:\Program Files\PostgreSQL\*\bin\libgeos_c.dll')

    if gdal_candidates:
        GDAL_LIBRARY_PATH = gdal_candidates[0]
    if geos_candidates:
        GEOS_LIBRARY_PATH = geos_candidates[0]
# else: trên Linux (Render), GDAL được cài qua build.sh, không cần set path


# ==============================================================
# CKEDITOR
# ==============================================================

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',
        ]),
    },
}