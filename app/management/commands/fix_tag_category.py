from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, Topic, Category


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        raw_category, _ = Category.objects.get_or_create(name="Raw")
        domain_category, _ = Category.objects.get_or_create(name="Domain")
        language_category, _ = Category.objects.get_or_create(name="Language")

        raw_topics = Topic.objects.filter(category=raw_category)
        for raw_topic in raw_topics:
            print(raw_topic.display_name)
            domain_topics = Topic.objects.filter(
                category=domain_category, display_name=raw_topic.display_name
            )
            present = False

            if domain_topics:
                domain_topic = domain_topics[0]
                posts = raw_topic.posts.all()
                for post in posts:
                    post.topics.remove(raw_topic)
                    post.topics.add(domain_topic)
                    print("Removed and addeed")
                present = True

            domain_topics = Topic.objects.filter(
                category=language_category, display_name=raw_topic.display_name
            )
            if domain_topics:
                domain_topic = domain_topics[0]
                posts = raw_topic.posts.all()
                for post in posts:
                    post.topics.remove(raw_topic)
                    post.topics.add(domain_topic)
                    print("Removed and addeed")
                present = True
            if present:
                raw_topic.delete()
