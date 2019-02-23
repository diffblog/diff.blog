from django.db import models
from django.contrib.auth.models import AbstractUser, User

# Create your models here.

class Topic(models.Model):
    name = models.TextField()
class UserProfile(models.Model):
    extra_data = models.TextField()
    auth = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="profile")
    feed_url = models.CharField(max_length=200)
    github_username = models.CharField(max_length=50)
    github_id = models.IntegerField()
    github_token = models.CharField(max_length=50, null=True)
    is_activated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50)
    topics = models.ManyToManyField(Topic)

class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)
    upvotes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "content": self.content,
            "updated_on": self.updated_on,
            "upvotes_count": self.upvotes_count,
            "comments_count": self.comments_count,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            }
        }

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            },
            "post_id": self.post.id,
        }
