from django.contrib import admin
from jobs.models import Location, Job
from app.admin import show_all_admin_fields

admin.site.register(Location, show_all_admin_fields(Location))
admin.site.register(Job, show_all_admin_fields(Job))
