from django.core.management.base import BaseCommand, CommandError

from app.models import Post

class Command(BaseCommand):
    help = 'Update aggregate vote count and score of all posts'

    def handle(self, *args, **options):
        posts = Post.objects.all()
        for post in posts:
            post.update_aggregate_votes_count_and_score()
