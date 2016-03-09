# -*- encoding:utf-8 -*-

from agenda.settings import *

# SECURITY
SECRET_KEY = '<doit être défini et complexe - 50 caractères sans accents>'
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['agenda.accoord.fr', '127.0.0.1']

# EMAIL CONFIGURATION
ENABLE_MAIL = True
FROM_EMAIL = 'vincent.correze@accoord.fr'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# DATABASE CONFIGURATION
DATABASES = {
    "default": {
        # PostgreSQL - See https://docs.djangoproject.com/en/1.9/ref/databases/#postgresql-notes
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": 'agendadulibre',
        "USER": 'agendadulibre',
        "PASSWORD": '*********',
        "HOST": '127.0.0.1',
        "PORT": '',
        }
}
