from app.models import Post
from django.utils import timezone
from datetime import timedelta

def get_posts_for_weekly_digest():
    time_cutoff = timezone.now() - timedelta(days=7)
    return Post.objects.filter(updated_on__gte=time_cutoff).order_by("-aggregate_votes_count")[:10]
