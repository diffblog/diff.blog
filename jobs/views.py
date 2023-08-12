from django.shortcuts import render

from jobs.models import Location
from app.models import Topic
from jobs.models import Job
from jobs.lib import get_latest_jobs


def jobs_directory(request, location_slug="", title_slug=""):
    location = None
    if location_slug:
        location = Location.objects.filter(slug=location_slug).last()

    title = title_slug
    if title_slug is not None:
        job = Job.objects.filter(title_slug=title_slug).first()
        if job is not None:
            title = job.title

    jobs = get_latest_jobs(location_slug, title_slug)
    return render(
        request,
        "jobs_directory.html",
        context={
            "location": location,
            "title_slug": title_slug,
            "jobs": jobs,
            "jobs_count": len(jobs),
            "title": title,
        },
    )


def job_form(request):
    if request.method == "GET":
        return render(request, "job_form.html")
    if request.method == "POST":
        locations_text = request.POST.get("locations")
        locations = []
        for location_text in locations_text.split(","):
            location, _ = Location.objects.get_or_create(
                name=location_text.lstrip().rstrip()
            )
            locations.append(location)
        job = Job.objects.create(
            company_name=request.POST.get("company-name"),
            company_url=request.POST.get("company-url"),
            title=request.POST.get("title"),
            description_link=request.POST.get("description-link"),
            source=Job.JOB_FORM_FREE,
        )
        job.locations.set(locations)
        profile = None
        if request.user.is_authenticated:
            profile = request.user.profile
        return render(request, "job_success.html")
