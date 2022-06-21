from django.core.cache import cache

from app.models import Post

def get_top_posts(topic, limit, last_post_score):
    min_votes = 20
    if topic:
        min_votes = 1
    query = Post.objects.filter(
        aggregate_votes_count__gte=min_votes, source=Post.RSS_FEED
    )
    if last_post_score is not None:
        query = query.filter(score__lte=last_post_score)
    if topic:
        query = query.filter(topics__slug=topic)
    query = query.order_by("-score")
    result = query.exclude(title__isnull=True).exclude(title="")[:limit]
    return cache.get_or_set(
        "top_{}_{}_{}".format(last_post_score, topic, limit), result
    )
