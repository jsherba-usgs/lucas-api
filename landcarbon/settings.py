import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

ADMINS = (
    ('gitdev', 'gitdev@localhost'),
)

MANAGERS = ADMINS

ALLOWED_HOSTS = ['52.9.202.136', '.landcarbon.org']

# SpatiaLite 4.3 path not found unless explicitly set.
SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': os.path.join(BASEDIR, '..', 'landcarbon.db'),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'corsheaders',
    'rest_framework',
    'spillway',
    'landcarbon.app',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True   

ROOT_URLCONF = 'landcarbon.urls'

TEMPLATES = [{
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
}]

WSGI_APPLICATION = 'landcarbon.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

'''CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        #'LOCATION': '/var/run/memcached/memcached.sock',
        'LOCATION': '127.0.0.1:11211',

    }
}
CACHE_MIDDLEWARE_KEY_PREFIX = 'landcarbon.org' '''

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cuc&w+s_^c=9m_4tbu198vf&_0#fvy$6d7i5fn-di=l8_!-1z0'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASEDIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASEDIR, 'static', 'public')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'

# Additional locations of static files
# STATICFILES_DIRS = (
    # path.join(PROJECT_ROOT, 'static', 'app'),
    # path.join(PROJECT_ROOT, 'static', 'build'),
# )

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_PAGINATION_CLASS': 'landcarbon.app.pagination.FeaturePagination',
    'PAGE_SIZE': 10,
}

try:
    from landcarbon.settings_local import *
except ImportError:
    pass
