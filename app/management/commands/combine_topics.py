from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, Topic, Category


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
       slugs = set(Topic.objects.filter().values_list("slug", flat=True))
       
       Topic.objects.filter(slug="").delete()
       
       for slug in slugs:
           topics = Topic.objects.filter(slug=slug)
           
           if len(topics) == 1:
               continue
           
           topic_to_keep = topics[0]
           for topic in topics[1:]:
                posts = Post.objects.filter(topics=topic)
                for post in posts:
                   post.topics.remove(topic)
                   post.topics.add(topic_to_keep)
                topic.delete()
