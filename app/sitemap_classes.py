from django.contrib.sitemaps import Sitemap
from app.models import Post, UserProfile, Topic

import datetime

class TopicSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Topic.objects.filter()

    def lastmod(self, topic):
        last_post = Post.objects.filter(topics=topic).last()
        if last_post is not None:
            return last_post.updated_on
        return None

    def changefreq(self, topic):
        last_post = Post.objects.filter(topics=topic).order_by('-updated_on').last()

        if last_post is None:
            return "monthly"

        today = datetime.datetime.now(datetime.timezone.utc)
        seconds_since_last_updated = (today - last_post.updated_on).total_seconds()

        if seconds_since_last_updated <= 60 * 60:
            return "hourly"

        if seconds_since_last_updated <= 60 * 60 * 24:
            return "daily"

        if seconds_since_last_updated <= 60 * 60 * 24 * 7:
            return "weekly"

        return "monthly"

class PostSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter()

    def lastmod(self, obj):
        return obj.updated_on

class UserSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return UserProfile.objects.filter()

sitemaps = {
    "post": PostSitemap,
    "user": UserSitemap,
    "tag": TopicSitemap
}
