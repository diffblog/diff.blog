from app.models import Topic
from django.core.cache import cache


def get_popular_topics():
    topics = Topic.objects.filter(is_popular=True)[:20]
    return sorted(topics, key=lambda x: x.slug)
