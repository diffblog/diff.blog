from django.db import models
from app.models import Topic


class Location(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

    def serialize(self):
        return {"name": self.name, "slug": self.slug}


class Job(models.Model):
    company_name = models.CharField(max_length=200)
    company_url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=300)
    locations = models.ManyToManyField(Location, related_name="jobs")
    posted_on = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)

    def serialize(self):
        return {
            "company_name": self.company_name,
            "company_url": self.company_url,
            "title": self.title,
            "url": self.url,
            "posted_on": self.posted_on.isoformat(),
            "locations": [location.serialize() for location in self.locations.all()],
        }
