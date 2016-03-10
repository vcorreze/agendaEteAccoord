# -*- encoding:utf-8 -*-

from agenda.settings import *

# SECURITY
SECRET_KEY = '<doit être défini et complexe - 50 caractères sans accents>'
DEBUG = True
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
# EMAIL BACKEND FOR TESTS - https://docs.djangoproject.com/en/dev/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/app-messages'  # change this to a proper location

# DATABASE CONFIGURATION
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.sqlite3',
        "NAME": 'agendadulibre.sqlite',
        "USER": 'agendadulibre',
        "PASSWORD": '',
        "HOST": '',
        "PORT": '',
        }
}
