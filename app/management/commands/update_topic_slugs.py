from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post

class Command(BaseCommand):
    help = 'Update slugs of all existing posts'

    def handle(self, *args, **options):
       topics = Topic.objects.all()
       for topic in topics:
           topic.save()
