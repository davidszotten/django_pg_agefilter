# Basic settings for test project

# Database settings. This assumes that the default user and empty
# password will work.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_pg_agefilter',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

SECRET_KEY = 'secret'

INSTALLED_APPS = (
    'tests.app',
)
