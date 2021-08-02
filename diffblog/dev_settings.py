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
CORS_ORIGIN_ALLOW_ALL = (
    True  # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
)
SITE_BASE_URL = "http://localhost:8000"
