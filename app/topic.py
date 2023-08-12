from app.models import Topic
from django.core.cache import cache
from django.conf import settings

def get_popular_topics():
    topics = Topic.objects.filter(is_popular=True)[:10]
    return sorted(topics, key=lambda x: x.slug)
