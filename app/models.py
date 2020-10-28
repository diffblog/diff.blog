from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import Sum
from django.utils.text import slugify

from datetime import datetime, timedelta
from math import log


class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Topic(models.Model):
    display_name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    recommended = models.ManyToManyField("UserProfile", related_name="recommended_in")
    slug = models.SlugField(unique=False, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.display_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

    def serialize(self):
        return {
            "display_name": self.display_name,
            "slug": self.slug,
        }

    def get_absolute_url(self):
        return "/tag/{}/new".format(self.slug)


class UserProfile(models.Model):
    extra_data = models.TextField()
    auth = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="profile"
    )
    feed_url = models.CharField(max_length=200)
    github_username = models.CharField(max_length=50)
    github_id = models.IntegerField(null=True)
    github_token = models.CharField(max_length=100, null=True)
    is_activated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50)
    topics = models.ManyToManyField(Topic, related_name="users")
    followers_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    blog_url = models.CharField(max_length=100, null=True)
    website_url = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True)
    company = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )
    is_organization = models.BooleanField(default=False)
    fetched_following_users = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    unsubscribe_key = models.CharField(max_length=50, null=True)
    send_weekly_digest_email = models.BooleanField(default=True)

    pocket_api_key = models.CharField(max_length=100, null=True)
    pocket_show_button = models.BooleanField(default=True)
    pocket_auto_save = models.BooleanField(default=False)

    FROM_GITHUB = 1
    FROM_GOOGLE = 2
    HANDPICKED = 3
    blog_url_type = models.IntegerField(null=True)

    FEED_PROCESSING = 1
    FEED_NOT_FOUND = 2
    FEED_ERROR = 3
    FEED_ACTIVATED = 4
    FEED_POSTS_NOT_FOUND = 5
    NO_BLOG_OR_FEED_URL = 6
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

    def __str__(self):
        return self.full_name

    @property
    def uri(self):
        return "https://diff.blog/" + self.github_username

    def get_absolute_url(self):
        return "/" + str(self.github_username)

    def unsubscribe_from_all_emails(self):
        self.send_weekly_digest_email = False
        self.save(update_fields=["send_weekly_digest_email"])


class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=300)
    summary = models.TextField(null=True)
    content = models.TextField()
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="posts"
    )
    updated_on = models.DateTimeField(null=True)
    upvotes_count = models.IntegerField(default=1)
    aggregate_votes_count = models.IntegerField(default=1)
    comments_count = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    topics = models.ManyToManyField(Topic, related_name="posts")
    slug = models.SlugField(unique=True, null=True, max_length=250)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = "{}-{}".format(slugify(self.title), str(self.id))
            self.save()

    def get_summary(self):
        # TODO: Don't stop the summary in between words.
        if not self.summary:
            return ""

        if len(self.summary) < 250:
            return self.summary
        return self.summary[:200] + "..."

    def serialize(self):
        topics = []
        for topic in self.topics.all()[:4]:
            if topic.display_name == "Uncategorized":
                continue
            topics.append(topic.serialize())

        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "slug": self.slug,
            "summary": self.get_summary(),
            "updated_on": self.updated_on.isoformat(),
            "score": self.score,
            "upvotes_count": self.upvotes_count,
            "aggregate_votes_count": self.aggregate_votes_count,
            "comments_count": self.comments_count,
            "topics": topics,
            "profile": {
                "github_username": self.profile.github_username,
                "full_name": self.profile.full_name,
            },
        }

    def get_mirror_votes(self):
        return self.mirror_posts.all().aggregate(Sum("votes"))["votes__sum"] or 0

    def update_aggregate_votes_count(self):
        self.aggregate_votes_count = self.upvotes_count + self.get_mirror_votes()
        self.save(update_fields=["aggregate_votes_count"])

    def update_score(self):
        def epoch_seconds():
            epoch = datetime(1970, 1, 1)
            td = self.updated_on.replace(tzinfo=None) - epoch
            return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

        s = self.aggregate_votes_count + 1
        order = log(s, 10)
        seconds = epoch_seconds() - 1134028003
        self.score = round(order + seconds / 45000, 7)
        self.save(update_fields=["score"])

    def update_aggregate_votes_count_and_score(self):
        self.update_aggregate_votes_count()
        self.update_score()

    def get_absolute_url(self):
        return "/post/" + str(self.slug)

    @property
    def uri(self):
        return "https://diff.blog/post/" + str(self.slug)


class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="votes"
    )


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


class BlogSuggestion(models.Model):
    username = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    suggested_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    PENDING = 0
    NO_GITHUB_ACCOUNT = 1
    ADDED = 10
    STATUS_CHOICES = {
        (0, "Pending"),
        (1, "No GitHub account"),
        (2, "No feed"),
        (3, "Should be added by the user"),
        (4, "Non English blog"),
        (10, "Blog added"),
    }
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)


class MirrorSource(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)


class MirrorPost(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="mirror_posts"
    )
    source = models.ForeignKey(
        MirrorSource, on_delete=models.CASCADE, related_name="mirror_posts"
    )
    votes = models.IntegerField(default=0)
    url = models.CharField(max_length=200)


class UserList(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="created_user_lists"
    )
    users = models.ManyToManyField("UserProfile", related_name="listed_in")
    slug = models.SlugField(unique=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)


class GitHubCampaign(models.Model):
    github_username = models.CharField(max_length=100)
    repo_name = models.CharField(max_length=150)
    ISSUE_CREATED_TO_ADD_BLOG_TO_DIFFBLOG = 60
    status = models.IntegerField()


class Search(models.Model):
    query = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="searches", null=True
    )

    def get_absolute_url(self):
        return "/search/{}".format(self.query.replace(" ", "+"))
