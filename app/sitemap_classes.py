from django.contrib.sitemaps import Sitemap
from app.models import Post, UserProfile, Topic, Search
from app.json_views.search import do_post_search
from jobs.models import Job, Location

import datetime


def get_changefreq_from_last_updated_time(updated_on):
    today = datetime.datetime.now(datetime.timezone.utc)
    seconds_since_last_updated = (today - updated_on).total_seconds()

    if seconds_since_last_updated <= 60 * 60:
        return "hourly"
    if seconds_since_last_updated <= 60 * 60 * 24:
        return "daily"
    if seconds_since_last_updated <= 60 * 60 * 24 * 7:
        return "weekly"
    return "monthly"


class TopicSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Topic.objects.filter()

    def lastmod(self, topic):
        return topic.updated_on

    def changefreq(self, topic):
        return get_changefreq_from_last_updated_time(topic.updated_on)


class CompanySitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Topic.objects.filter()

    def lastmod(self, topic):
        return topic.updated_on

    def changefreq(self, topic):
        return get_changefreq_from_last_updated_time(topic.updated_on)

    def location(self, topic):
        return "/companies/companies-using-{}".format(topic.slug)


class PostSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter()

    def lastmod(self, obj):
        return obj.updated_on


class UserSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return UserProfile.objects.filter()

    def lastmod(self, profile):
        return profile.last_post_date

    def changefreq(self, profile):
        if profile.last_post_date is None:
            return "monthly"

        return get_changefreq_from_last_updated_time(profile.last_post_date)


class JobsByLocationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Location.objects.filter()

    def lastmod(self, location):
        return datetime.datetime.now() - datetime.timedelta(days=1)

    def location(self, location):
        return "/jobs-in-{}".format(location.slug)


class JobsByTitleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Job.objects.all().values_list("title_slug", flat=True).distinct()

    def lastmod(self, title_slug):
        return datetime.datetime.now() - datetime.timedelta(days=1)

    def location(self, title_slug):
        return "/{}-jobs".format(title_slug)


class SearchSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Search.objects.filter().exclude(query__exact="")

    def lastmod(self, search):
        posts = do_post_search(search.query, 1)
        if posts:
            return posts[0].updated_on
        return None

    def changefreq(self, search):
        posts = do_post_search(search.query, 1)
        if posts:
            return get_changefreq_from_last_updated_time(posts[0].updated_on)
        return "monthly"


sitemaps = {
    "post": PostSitemap,
    "user": UserSitemap,
    "tag": TopicSitemap,
    "company": CompanySitemap,
    "jobs-by-location": JobsByLocationSitemap,
    "jobs-by-title": JobsByTitleSitemap,
}
