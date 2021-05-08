from app.models import Post
from django.utils import timezone
from datetime import timedelta


def get_posts_for_weekly_digest():
    time_cutoff = timezone.now() - timedelta(days=7)
    all_posts = Post.objects.filter(updated_on__gte=time_cutoff).order_by(
        "-aggregate_votes_count"
    )[:30]

    users_ids = set()
    posts = []
    for post in all_posts:
        if post.profile.id in users_ids:
            continue
        posts.append(post)
        users_ids.add(post.profile.id)

        if len(users_ids) == 10:
            break

    return posts
