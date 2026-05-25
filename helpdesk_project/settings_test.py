"""Settings override for CI/test — force SQLite, no external services."""
from helpdesk_project.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

OPENWEATHER_API_KEY = 'test_key'
