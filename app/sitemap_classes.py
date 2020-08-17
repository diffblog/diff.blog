from django.contrib.sitemaps import Sitemap
from app.models import Post

class PostSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter()

    def lastmod(self, obj):
        return obj.updated_on

sitemaps = {
    "post": PostSitemap,
}
