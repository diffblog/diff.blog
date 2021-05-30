from app.models import Post
from django.utils import timezone
from datetime import timedelta

cutoff_days = 7


def get_global_popular_posts_from_last_week(ignore_post_ids):
    time_cutoff = timezone.now() - timedelta(days=cutoff_days)
    all_posts = (
        Post.objects.filter(updated_on__gte=time_cutoff)
        .order_by("-aggregate_votes_count")
        .exclude(id__in=ignore_post_ids)[:30]
    )

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


def get_popular_posts_from_following_users_last_week(user_profile):
    time_cutoff = timezone.now() - timedelta(days=cutoff_days)
    all_posts = Post.objects.filter(
        updated_on__gte=time_cutoff, profile__in=user_profile.following.all(), aggregate_votes_count__gte=5
    ).order_by("-aggregate_votes_count")[:10]
    return list(all_posts)


def get_weekly_digest_posts(user_profile):
    following_posts = get_popular_posts_from_following_users_last_week(user_profile)
    following_post_ids = [post.id for post in following_posts]

    popular_posts = get_global_popular_posts_from_last_week(following_post_ids)
    return popular_posts, following_posts
