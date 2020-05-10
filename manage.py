#!/usr/bin/env python3.6
import os
import sys

if __name__ == "__main__":
    if os.environ["DEVELOPMENT"]:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diffblog.dev_settings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diffblog.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
