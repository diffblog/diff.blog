from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache

from app.models import Post

class Command(BaseCommand):
    help = 'Update aggregate vote count and score of all posts from last 1 week'

    def handle(self, *args, **options):
        three_days_back = timezone.now() - timedelta(days=7)
        posts = Post.objects.filter(updated_on__gte=three_days_back)

        for post in posts:
            post.update_aggregate_votes_count_and_score()
        cache.delete('top')
