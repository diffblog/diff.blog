import os

from diffblog.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEVELOPMENT = True
DEBUG = True

ALLOWED_HOSTS = ["localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "diffblog",
        "USER": "postgres",
        "PASSWORD": "postgres_password",
        "HOST": "db",
        "PORT": "",
    }
}

LOGGING = {}
