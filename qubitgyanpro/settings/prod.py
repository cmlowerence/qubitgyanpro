from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES['default']['NAME'] = BASE_DIR / 'db.sqlite3'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING['root']['level'] = 'DEBUG'