"""
Django settings for simple_newsletter project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)

STATIC_URL = '/static/'


# Set up django-environ
env = environ.Env(
    # Default values for variables if not set
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')

RECAPTCHA_REQUIRED_SCORE = 0.85

MEDIA_ROOT = '/opt/media/simple_newsletter/media/'
MEDIA_URL = '/media/'

BASE_URL = env('BASE_URL')

CKEDITOR_UPLOAD_PATH = 'content/ckeditor/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        # ... any additional CKEditor options you want to include ...
    },
}

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Update this to your Redis broker URL
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


if NOTIFICATION_BCC_RECIPIENTS := env('NOTIFICATION_BCC_RECIPIENTS'):
    NOTIFICATION_BCC_RECIPIENTS = [email.strip() for email in NOTIFICATION_BCC_RECIPIENTS.split(',')]
else:
    NOTIFICATION_BCC_RECIPIENTS = None


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_recaptcha',
    'core',
    'bootstrap5',
    'ckeditor',
    'ckeditor_uploader',

    # see also:
    # https://django-two-factor-auth.readthedocs.io/en/stable/installation.html
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_email',  # <- if you want email capability.
    'two_factor',
    'two_factor.plugins.phonenumber',  # <- if you want phone number capability.
    'two_factor.plugins.email',  # <- if you want email capability.
    # 'two_factor.plugins.yubikey',  # <- for yubikey capability.
    'debug_toolbar',
]

# rechapcha settings:
# https://www.google.com/recaptcha/admin

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # see also:
    # https://django-two-factor-auth.readthedocs.io/en/stable/installation.html
    'django_otp.middleware.OTPMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'simple_newsletter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'simple_newsletter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# generate sql script to create database and user with generate_sql_script.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='127.0.0.1'),  # default to localhost if DB_HOST is not set
        'PORT': env('DB_PORT', default='3306'),  # default to 3306 if DB_PORT is not set
        'AUTOCOMMIT': True,
        'OPTIONS': {'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
        # https://code.djangoproject.com/ticket/18392
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


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# For local testing purposes, you can use the console backend which prints emails to the console instead of sending them:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# see also:
# https://django-two-factor-auth.readthedocs.io/en/stable/installation.html
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'two_factor:profile'

LOGOUT_REDIRECT_URL = 'home'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}