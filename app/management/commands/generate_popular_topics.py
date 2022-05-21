import pdb
from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, Topic, Category
from django.core.cache import cache

from collections import Counter

EXCLUDED_TOPICS = set(
    [
        "uncategorized",
        "news",
        "article",
        "link",
        "sponsored",
        "articles",
        "engineering",
        "tech",
    ]
)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        posts = Post.objects.filter().order_by("-id")[:10000]
        counter = Counter()

        for post in posts:
            for topic in post.topics.all():
                counter[topic.slug] += 1

        for topic in Topic.objects.filter(is_popular=True):
            topic.is_popular = False
            topic.save()

        for topic_slug, _ in counter.most_common()[:100]:
            if topic_slug in EXCLUDED_TOPICS:
                continue
            topic = Topic.objects.filter(slug=topic_slug)[0]
            topic.is_popular = True
            topic.save()
