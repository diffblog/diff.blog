from django.core.cache import cache
from django.db.models import Q

from app.models import Post


def basic_post_filter(query, last_post_score, limit):
    query = query.filter(source=Post.RSS_FEED)
    if last_post_score is not None:
        query = query.filter(score__lte=last_post_score)
    query = query.order_by("-score")
    return query.exclude(title__isnull=True).exclude(title="")[:limit]


def get_top_posts(topic, limit, last_post_score):
    if topic:
        query = Post.objects.filter(topics__slug=topic)
    else:
        query = Post.objects.filter(aggregate_votes_count__gte=20)

    result = basic_post_filter(query, last_post_score, limit)
    return cache.get_or_set(
        "top_{}_{}_{}".format(last_post_score, topic, limit), result
    )


def get_top_posts_for_user(profile, limit, last_post_score):
    MIN_VOTES = 50

    query = Post.objects.filter(
        Q(topics__in=profile.topics.all(), aggregate_votes_count__gte=2)
        | Q(profile__in=profile.following.all())
        | Q(aggregate_votes_count__gte=MIN_VOTES)
    )
    return basic_post_filter(query, last_post_score, limit)
