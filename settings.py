# Django settings for crowdata project.

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
     ('', ''),
)

MANAGERS = ADMINS



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'somethinguniqueandnotshareitwithanybody'

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'crowdataapp.middleware.LocalUserMiddleware',
    'pagination.middleware.PaginationMiddleware',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
ROOT_URLCONF = 'crowdata.urls'

TEMPLATE_CONTEXT_PROCESSORS = [
    # other context processors
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
]

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates')
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

FORMS_BUILDER_USE_HTML5  = True


INSTALLED_APPS = [
    'admintheme',
    'django.contrib.auth',
    'django_browserid', # mozilla persona
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    'nested_inlines',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_extensions',
    'forms_builder.forms',
    'south',
    'django_ace',
    'djorm_pgtrgm',
    'pagination',
    'crowdata.crowdataapp',
]


AUTHENTICATION_BACKENDS = (
   'django.contrib.auth.backends.ModelBackend',
   'django_browserid.auth.BrowserIDBackend',
)


LOGGING = {
    'version': 1,
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '':  {
            'handlers': ['console'],
            'level': 'DEBUG',
        },

        'django.db': {
        },
    },
 }

SITE_URL = 'http://localhost:8000'
LOGIN_URL = '/cd/pleaselogin'
LOGIN_REDIRECT_URL = '/cd/afterlogin'
LOGOUT_REDIRECT_URL = '/cd'
LOGIN_REDIRECT_URL_FAILURE = '/cd/loginfailure'

AUTH_PROFILE_MODULE = 'crowdataapp.UserProfile'

try:
    from local_settings import *
except ImportError:
    pass
