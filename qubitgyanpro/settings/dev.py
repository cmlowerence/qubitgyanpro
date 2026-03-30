from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Local dev database (same as base or override if needed)
DATABASES['default']['NAME'] = BASE_DIR / 'db.sqlite3'

# Enable browsable API (VERY IMPORTANT for dev)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Disable strict security
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Email backend (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging more verbose
LOGGING['root']['level'] = 'DEBUG'