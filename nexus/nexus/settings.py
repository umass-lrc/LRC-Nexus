"""
Django settings for nexus project.

Generated by "django-admin startproject" using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

from django.contrib import messages

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("NEXUS_SECRET_KEY", "django-insecure-881r(ved7o)qr@@bkmapeg2ca88p1c&9^y*=5v9rwf9*0%%q%$")

ALLOWED_HOSTS = os.environ.get("NEXUS_ALLOWED_HOSTS", ".localhost,127.0.0.1,[::1]").split(",")

CSRF_TRUSTED_ORIGINS = ["http://3.137.183.137:80", "https://www.umass.edu"]

CORS_ORIGIN_WHITELIST = ["http://3.137.183.137:80", "https://www.umass.edu"]

CORS_ALLOWED_ORIGINS = ["https://www.umass.edu"]

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = os.environ.get("NEXUS_DEBUG", "0") == "1"


# Application definition

INSTALLED_APPS = [
    # Installed apps
    "dal",
    "dal_select2",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Installed apps
    "crispy_forms",
    "crispy_bootstrap5",
    "corsheaders",
    "explorer",
    "tinymce",
    "django_elasticsearch_dsl",
    "hijack",
    # Local apps
    "core",
    "users",
    "patches",
    "shifts",
    "payrolls",
    "SIs",
    "tutors",
    "students",
    "htmx_apis",
    "ours",
    "oa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Installed middleware for cross origin requests
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Local middleware
    "hijack.middleware.HijackUserMiddleware",
]

ROOT_URLCONF = "nexus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR.joinpath("core", "templates"),
            BASE_DIR.joinpath("users", "templates"),
            BASE_DIR.joinpath("patches", "templates"),
            BASE_DIR.joinpath("shifts", "templates"),
            BASE_DIR.joinpath("SIs", "templates"),
            BASE_DIR.joinpath("students", "templates"),
            BASE_DIR.joinpath("payrolls", "templates"),
            BASE_DIR.joinpath("tutors", "templates"),
            BASE_DIR.joinpath("htmx_apis", "templates"),
            BASE_DIR.joinpath("ours", "templates"),
            BASE_DIR.joinpath("oa", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Local context processors
            ],
        },
    },
]

WSGI_APPLICATION = "nexus.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database.sqlite3",
    }
}

# Cache
# https://docs.djangoproject.com/en/5.0/topics/cache/

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

AUTH_USER_MODEL = "users.NexusUser"
LOGIN_URL = '/users/login'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy Forms

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

# Exlorer for SQL queries
EXPLORER_CONNECTIONS = {'default': 'default'}
EXPLORER_DEFAULT_CONNECTION = 'default'

EXPLORER_SQL_BLACKLIST = ()

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: "primary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

TINYMCE_JS_URL = "tinymce/tinymce.min.js"
TINYMCE_JS_ROOT = "tinymce/"
TINYMCE_SPELLCHECKER = False


ELASTICSEARCH_DSL={
    'default': {
        'hosts': 'http://es-nexus:9200', 
        'http_auth': ('elastic', 'es4lrcnexus'), #os.environ.get("ELASTIC_PASSWORD", "ES4LRC!!")
        # 'ssl_assert_fingerprint': os.environ.get("ES_SSL", '91d3dcd44b40de733de0e099f71a0b5a74af7a0c4697cbdc5646bc01974f12c8'),
    }
}