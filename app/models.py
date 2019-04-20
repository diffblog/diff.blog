from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core import serializers
from datetime import datetime, timedelta
from math import log
from django.forms.models import model_to_dict

class Category(models.Model):
    name = models.CharField(max_length=30)

class Topic(models.Model):
    display_name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    recommended = models.ManyToManyField("UserProfile", related_name="reccomended_in")

    def serialize(self):
        return {
            "display_name": self.display_name,
        }

class UserProfile(models.Model):
    extra_data = models.TextField()
    auth = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="profile")
    feed_url = models.CharField(max_length=200)
    github_username = models.CharField(max_length=50)
    github_id = models.IntegerField(null=True)
    github_token = models.CharField(max_length=50, null=True)
    is_activated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50)
    topics = models.ManyToManyField(Topic, related_name="users")
    followers_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    blog_url = models.CharField(max_length=100, null=True)
    website_url = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    company = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=50, null=True)
    following = models.ManyToManyField("self", related_name="followers", symmetrical=False)
    is_organization = models.BooleanField(default=False)
    fetched_following_users = models.BooleanField(default=False)

    FROM_GITHUB = 1
    FROM_GOOGLE = 2
    HANDPICKED = 3
    blog_url_type = models.IntegerField(null=True)

    FEED_PROCESSING = 1
    FEED_NOT_FOUND = 2
    FEED_ERROR = 3
    FEED_ACTIVATED = 4
    FEED_POSTS_NOT_FOUND = 5
    feed_status = models.IntegerField(null=True)

    def serialize(self, get_topics=False):
        topics = []
        if get_topics:
            for topic in self.topics.all():
                topics.append(topic.serialize())

        return {
            "id": self.id,
            "full_name": self.full_name,
            "github_username": self.github_username,
            "company": self.company,
            "bio": self.bio,
            "topics": topics,
        }

class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    summary = models.TextField(null=True)
    content = models.TextField()
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)
    upvotes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def get_summary(self):
        #TODO: Don't stop the summary in between words.
        if len(self.summary) < 250:
            return self.summary
        return self.summary[:200] + "..."

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "summary": self.get_summary(),
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
