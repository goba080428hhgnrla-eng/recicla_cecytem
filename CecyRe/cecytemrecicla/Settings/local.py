from .base import *
from pathlib import Path

DEBUG = True

ALLOWED_HOSTS = [
    'https://recicla-cecytem.onrender.com',
    'localhost',
    '127.0.0.1',
]

ROOT_URLCONF = 'cecytemrecicla.urls'


DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}


STATIC_URL = '/static/'

STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles')
 
STATICFILES_DIRS = [
    BASE_DIR / 'static',  
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
