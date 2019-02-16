from django.db import models
from django.contrib import admin

from app.models import UserProfile

class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "content": self.content,
            "updated_on": self.updated_on,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            }
        }
