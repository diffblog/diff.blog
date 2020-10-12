from django.contrib.sitemaps import Sitemap
from app.models import Post, UserProfile

import datetime

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
}
