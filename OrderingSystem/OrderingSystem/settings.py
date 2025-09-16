"""
Django settings for OrderingSystem project.
Modified for Render deployment with Daphne, Channels, and Redis.
Optimized for Render deployment with Daphne, Channels, and Redis.
"""

import os
import dj_database_url  
import redis
from pathlib import Path
import dj_database_url

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Security
# --------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-fallback-key")

DEBUG = os.environ.get("DEBUG", "False").lower() in ["true", "1"]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "orderingsystem-b1.onrender.com").split(",")

# --------------------------------------------------
# Applications
# --------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'channels',

    # Local
    'MSMEOrderingWebApp.apps.MSMEOrderingWebAppConfig',
]

# --------------------------------------------------
# ASGI / Channels
# --------------------------------------------------
ASGI_APPLICATION = 'OrderingSystem.asgi.application'

REDIS_URL = os.environ.get("REDIS_URL", None)

if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.environ.get("REDIS_URL", "redis://red-d34h8numcj7s73cscpc0:6379/0")],
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Fallback (for local dev)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

# --------------------------------------------------
# Middleware
# --------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Custom middleware (must be early)
    'MSMEOrderingWebApp.middleware.BusinessOwnerSetupMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# --------------------------------------------------
# URLs / Templates
# --------------------------------------------------
ROOT_URLCONF = 'OrderingSystem.urls'


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

WSGI_APPLICATION = 'OrderingSystem.wsgi.application'

# --------------------------------------------------
# Database
# --------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

# --------------------------------------------------
# Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Manila")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# Static & Media Files
# --------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL= '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'MSMEOrderingWebApp/static')
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --------------------------------------------------
# Default Primary Key
# --------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# Development: serve media files in DEBUG mode
# --------------------------------------------------
if DEBUG:
    from django.conf.urls.static import static
    from django.urls import re_path

    urlpatterns = [
        # your urls go here
    ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
