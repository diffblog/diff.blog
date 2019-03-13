from django.db import models
from django.contrib.auth.models import AbstractUser, User
from datetime import datetime, timedelta
from math import log


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
    followers_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    blog_url = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    company = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=50, null=True)
    following = models.ManyToManyField("self", related_name="followers", symmetrical=False)

    FROM_GITHUB = 1
    FROM_GOOGLE = 2
    HANDPICKED = 3
    blog_url_type = models.IntegerField(null=True)

    PROCESSING = 1
    ACTIVE = 2
    NOT_FOUND = 3
    ERROR = 4
    feed_status = models.IntegerField(null=True)

    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "github_username": self.github_username,
            "company": self.company,
            "bio": self.bio,
        }

class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)
    upvotes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "content": self.content,
            "updated_on": self.updated_on.isoformat(),
            "score": self.score,
            "upvotes_count": self.upvotes_count,
            "comments_count": self.comments_count,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            }
        }

    def update_score(self):
        def epoch_seconds():
            epoch = datetime(1970, 1, 1)
            td = self.updated_on.replace(tzinfo=None) - epoch
            return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

        s = self.upvotes_count - 0
        order = log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else -1 if s < 0 else 0
        seconds = epoch_seconds() - 1134028003
        self.score = round(sign * order + seconds / 45000, 7)
        self.save(update_fields=['score'])

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)
    upvotes_count = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            },
            "post_id": self.post.id,
            "posted_on": self.posted_on.isoformat(),
            "upvotes_count": self.upvotes_count,
        }

class CommentVote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
