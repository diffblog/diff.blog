from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from dateutil.parser import parse as iso_date_parser
from app.json_views.posts import get_top_posts, get_top_posts_for_user

from app.models import Vote, Post


def set_user_votes(request, posts):
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(profile=request.user.profile).values_list(
            "post__id", flat=True
        )
    else:
        user_votes = []
    for post in posts:
        if post["id"] in user_votes:
            post["upvoted"] = True
        else:
            post["upvoted"] = False


def get_posts(request, feed_type):
    topic = request.GET.get("topic", None)
    limit = int(request.GET.get("limit", 30))
    logged_in = request.user.is_authenticated

    if feed_type == "top":
        last_post_score = request.GET.get("last_post_score", None)
        if logged_in and not topic:
            posts = get_top_posts_for_user(request.user.profile, limit, last_post_score)
        else:
            posts = get_top_posts(topic, limit, last_post_score)

    if feed_type == "new":
        query = Post.objects.filter(source=Post.RSS_FEED)
        last_post_date = request.GET.get("last_post_updated_on", None)
        if last_post_date is not None:
            last_post_date = iso_date_parser(last_post_date)
            query = query.filter(updated_on__lte=last_post_date)
        if topic:
            query = query.filter(topics__slug=topic)
        query = query.filter(Q(language='en') | Q(language__isnull=True))
        query = query.order_by("-updated_on")
        posts = query.exclude(title__isnull=True).exclude(title="")[:limit]

    if feed_type == "following":
        if not request.user.is_authenticated:
            posts = []
        else:
            query = Post.objects.filter(
                profile__in=request.user.profile.following.all(), source=Post.RSS_FEED
            )
            last_post_date = request.GET.get("last_post_updated_on", None)
            if last_post_date is not None:
                last_post_date = iso_date_parser(last_post_date)
                query = query.filter(updated_on__lte=last_post_date)
            if topic:
                query = query.filter(topics__slug=topic)
            query = query.order_by("-updated_on")
            posts = query.exclude(title__isnull=True).exclude(title="")[:limit]

    if feed_type == "recommended":
        if not request.user.is_authenticated:
            posts = []
        else:
            # Currently fetching posts from users who has similar topics
            # in their profile. In future can do intesrting things like
            # getting the liked posts of people the user follow and all.
            last_post_date = request.GET.get("last_post_updated_on", None)

            following_user_ids = list(
                request.user.profile.following.all()
                .values_list("id", flat=True)
                .order_by("id")
            )
            following_user_ids.append(request.user.profile.id)
            similar_users = []
            for topic in request.user.profile.topics.all():
                similar_users.extend(
                    topic.users.filter().exclude(id__in=following_user_ids)
                )

            if last_post_date is not None:
                last_post_date = iso_date_parser(last_post_date)
                posts = Post.objects.filter(
                    updated_on__lte=last_post_date, profile__in=similar_users
                ).order_by("-updated_on")[:limit]
            else:
                posts = Post.objects.filter(profile__in=similar_users).order_by(
                    "-updated_on"
                )[:limit]

    if feed_type == "user":
        username = request.GET.get("username", None)
        query = Post.objects.filter(
            profile__github_username=username, source=Post.RSS_FEED
        )
        last_post_date = request.GET.get("last_post_updated_on", None)
        if last_post_date is not None:
            last_post_date = iso_date_parser(last_post_date)
            query = query.filter(updated_on__lte=last_post_date)
        query = query.order_by("-updated_on")
        posts = query[:limit]

    if feed_type == "liked":
        username = request.GET.get("username", None)
        post_ids = Vote.objects.filter(profile__github_username=username).values_list(
            "post__id", flat=True
        )
        query = Post.objects.filter(id__in=post_ids)

        last_post_date = request.GET.get("last_post_updated_on", None)
        if last_post_date is not None:
            last_post_date = iso_date_parser(last_post_date)
            query = query.filter(updated_on__lte=last_post_date)
        query = query.order_by("-updated_on")
        posts = query[:limit]

    posts = [post.serialize() for post in posts]
    set_user_votes(request, posts)
    return JsonResponse(posts, safe=False)


def get_user_votes(request):
    votes = Vote.objects.filter(profile=request.user.profile)
    return JsonResponse([{"post_id": votes.post.id for vote in votes}], safe=False)


@login_required
def upvote_or_downvote_post(request):
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    try:
        vote = Vote.objects.get(post=post, profile=request.user.profile)
        vote.delete()
        post.upvotes_count = post.upvotes_count - 1
        post.save()
        post.update_aggregate_votes_count_and_score()
    except Vote.DoesNotExist:
        Vote.objects.create(post=post, profile=request.user.profile)
        post.upvotes_count = post.upvotes_count + 1
        post.save()
        post.update_aggregate_votes_count_and_score()
    return JsonResponse("Success", safe=False)
