import pdb
from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, Topic, Category
from django.core.cache import cache

from collections import Counter

class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        posts = Post.objects.filter().order_by('id')[:1000]
        counter = Counter()
       
        for post in posts:
            for topic in post.topics.all():
               counter[topic.slug] += 1
        
        topics = []
        for topic_slug, _ in counter.most_common()[:100]:
            topic = Topic.objects.filter(slug=topic_slug)[0]
            topics.append(topic)
            
        cache.set("popular_topics", topics, timeout=None)
