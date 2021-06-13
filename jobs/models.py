from django.db import models
from app.models import Topic
from django.utils.text import slugify


class Location(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, max_length=200)

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

    def serialize(self):
        return {"name": self.name, "slug": self.slug}


class Job(models.Model):
    company_name = models.CharField(max_length=200)
    company_url = models.CharField(max_length=200, null=True)
    title = models.CharField(max_length=200)
    title_slug = models.SlugField(max_length=200, null=True)
    description_link = models.CharField(max_length=300)
    locations = models.ManyToManyField(Location, related_name="jobs")
    posted_on = models.DateTimeField(auto_now_add=True)
    github_username = models.CharField(max_length=200, null=True)

    JOB_FORM_FREE = 1
    JOB_FORM_PAID = 10
    GREENHOUSE = 100
    source = models.IntegerField(null=True)
    global_job_id = models.CharField(max_length=200, null=True)

    def save(self, *args, **kwargs):
        self.title_slug = self.title_slug or slugify(self.title)
        super().save(*args, **kwargs)

    def get_company_logo_url(self):
        if self.company_url:
            return "https://logo.clearbit.com/" + self.company_url
        return "https://avatars.githubusercontent.com/" + self.github_username

    def get_company_url(self):
        if self.company_url:
            return self.company_url
        return "https://diff.blog/" + self.github_username

    def serialize(self):
        return {
            "company_name": self.company_name,
            "company_url": self.get_company_url(),
            "company_logo_url": self.get_company_logo_url(),
            "title": self.title,
            "description_link": self.description_link,
            "posted_on": self.posted_on.isoformat(),
            "locations": [location.serialize() for location in self.locations.all()],
        }
