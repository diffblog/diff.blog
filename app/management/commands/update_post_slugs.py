from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post


class Command(BaseCommand):
    help = "Update slugs of all existing posts"

    def handle(self, *args, **options):
        posts = Post.objects.all()
        for post in posts:
            post.save()
