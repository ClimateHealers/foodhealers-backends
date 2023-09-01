"""
Django settings for foodhealers_backend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import firebase_admin
from firebase_admin import credentials


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR / "app"
APPS_DIR = BASE_DIR / "usermgmnt"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m+rp2up2513j@sq+^qdu&*y%9v1-sk*x2mwm-pq%_7s)c=pzv%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', 'api.climatehealers.com', '127.0.0.1', '*']

CSRF_TRUSTED_ORIGINS = ['https://api.climatehealers.com','https://*.127.0.0.1', 'https://foodhealers.climatehealers.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_swagger',
    'drf_yasg',
    'app',
    'corsheaders',
    'taggit',
    'rest_framework.authtoken',
    'debug_toolbar',
    'django_celery_beat',
    'django_celery_results',
    'analytical',
    'django_matplotlib',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'foodhealers_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR/"templates")],
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

WSGI_APPLICATION = 'foodhealers_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Database
# Load environment variables from .local.env
env_file_path = os.path.join(os.environ['HOME'], '.local.env')

with open(env_file_path) as f:
    for line in f:
        line = line.strip() 
        if line and not line.startswith("#"): 
            key, value = line.split("=", 1) 
            os.environ[key] = value

# Access the environment variables
db_engine = os.getenv('DB_ENGINE')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
GOOGLE_MAPS_API_KEY = os.getenv('API_KEY')
firebase_admin_sdk_file = os.getenv('FIREBASE_ADMIN_SDK')
MIXPANEL_API_TOKEN = os.getenv('MIXPANEL_TOKEN')
S3_AWS_ACCESS_KEY_ID = os.getenv('S3_AWS_ACCESS_KEY_ID')
S3_AWS_SECRET_ACCESS_KEY = os.getenv('S3_AWS_SECRET_ACCESS_KEY')
S3_AWS_MEDIA_ACCESS_KEY_ID = os.getenv('S3_AWS_MEDIA_ACCESS_KEY_ID')
S3_AWS_MEDIA_SECRET_ACCESS_KEY = os.getenv('S3_AWS_MEDIA_SECRET_ACCESS_KEY')
EMAIL_SENDINBLUE_API_KEY = os.getenv('EMAIL_SENDINBLUE_API_KEY')
SENDINBLUE_EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
VOLUNTEER_PASSWORD = os.getenv('VOLUNTEER_PASSWORD')

# Use the environment variables in your Django settings
DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,
        'PORT': db_port,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Static File Settings 
STATIC_ROOT = os.path.join(BASE_DIR, "static")

AWS_ACCESS_KEY_ID = S3_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = S3_AWS_SECRET_ACCESS_KEY
AWS_S3_OBJECT_PARAMETERS = {
   ' CacheControl' : 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'foodhealers-static-files-django'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_LOCATION = 'static'
AWS_S3_REGION_NAME = 'ap-south-1'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# firebase admin initialization
cred = credentials.Certificate(firebase_admin_sdk_file)
firebase_admin.initialize_app(cred)

# Media File Settings
# Managing  image
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media/')
MEDIA_URL = '/media/'

AWS_ACCESS_KEY_ID = S3_AWS_MEDIA_ACCESS_KEY_ID 
AWS_SECRET_ACCESS_KEY = S3_AWS_MEDIA_SECRET_ACCESS_KEY
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS__MEDIA_STORAGE_BUCKET_NAME = 'foodhealers-media-files'
AWS_S3_MEDIA_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS__MEDIA_STORAGE_BUCKET_NAME
AWS_MEDIA_LOCATION = 'media'
AWS_S3_MEDIA_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS__MEDIA_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
MEDIA_URL = 'https://%s/%s/' % (AWS_S3_MEDIA_CUSTOM_DOMAIN, AWS_MEDIA_LOCATION)

# # AWS Email Settings
# AWS_ACCESS_KEY_ID = EMAIL_AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY = EMAIL_AWS_SECRET_ACCESS_KEY
# DEFAULT_SENDER = EMAIL_AWS_DEFAULT_SENDER
# EMAIL_BACKEND = 'django_amazon_ses.EmailBackend'
# AWS_DEFAULT_REGION=EMAIL_AWS_DEFAULT_REGION
# EMAIL_PORT = 587

# Send in Blue Settings
SENDINBLUE_API_KEY = EMAIL_SENDINBLUE_API_KEY
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_HOST_USER = 'climatehealers@climatehealers.org'
EMAIL_HOST_PASSWORD = SENDINBLUE_EMAIL_HOST_PASSWORD
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_SENDER = 'climatehealers@climatehealers.org'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# REST FRAMEWORK SETTINGS
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
       # 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # the number of items displayed per page
}

# celery configuration
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_ENABLED = True

PRODUCTION_URL = 'https://foodhealers.climatehealers.com'
DEPLOYED_URL = 'https://api.climatehealers.com'
LOCAL_URL = 'http://127.0.0.1:8000'
