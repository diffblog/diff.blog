from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

from app.models import Topic
from jobs.lib import get_latest_jobs
from jobs.models import Location


def jobs(request):
    if request.method == "GET":
        jobs = [
            job.serialize() for job in get_latest_jobs(request.GET.get("location_slug"))
        ]
        return JsonResponse(jobs, safe=False)
