from django.contrib.sitemaps import Sitemap
from app.models import Post, UserProfile, Topic

import datetime

class TopicSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Topic.objects.filter()

    def lastmod(self, topic):
        last_post = Post.objects.filter(topics=topic).last()
        if last_post is not None:
            return last_post.updated_on
        return None

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
