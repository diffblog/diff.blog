from jobs.models import Job


def get_latest_jobs(location_slug=None, title_slug=None, limit=200):
    jobs = Job.objects.filter()
    if location_slug:
        jobs = jobs.filter(locations__slug=location_slug)
    if title_slug:
        jobs = jobs.filter(title_slug__contains=title_slug)
    jobs = jobs.order_by("-posted_on")
    jobs = jobs[:limit]
    return jobs
