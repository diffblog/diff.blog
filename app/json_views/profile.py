from datetime import timedelta

from django.shortcuts import render
from django.http import JsonResponse
from django.http import QueryDict
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

import json
import logging
import random

from app.models import Vote, Post, Comment, UserProfile, Topic, get_topic
from app.queue import add_feed_initializer_to_queue

logger = logging.getLogger(__name__)


def serialize_users(request, users, get_topics=False):
    if request.user.is_authenticated:
        following = request.user.profile.following.all()
    else:
        following = []
    serialized_users = []
    for user in users:
        serialized_user = user.serialize(get_topics)
        if not request.user.is_authenticated:
            serialized_user["is_following"] = False
        elif user == request.user.profile:
            serialized_user["is_me"] = True
        elif user in following:
            serialized_user["following"] = True
        else:
            serialized_user["following"] = False
        serialized_users.append(serialized_user)
    return serialized_users


def following_users(request):
    if request.method == "GET":
        user_profile = UserProfile.objects.get(
            github_username=request.GET.get("username", None)
        )
        following = user_profile.following.all()
        serialized_users = serialize_users(request, following)
        return JsonResponse(serialized_users, safe=False)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        followed_user = UserProfile.objects.get(id=user_id)
        request.user.profile.following.add(followed_user)
        return JsonResponse("Success", safe=False)

    if request.method == "DELETE":
        data = QueryDict(request.body)
        user_id = data.get("user_id")
        unfollowed_user = UserProfile.objects.get(id=user_id)
        request.user.profile.following.remove(unfollowed_user)
        return JsonResponse("Success", safe=False)


def follower_users(request):
    user_profile = UserProfile.objects.get(
        github_username=request.GET.get("username", None)
    )
    followers = user_profile.followers.all()
    serialized_users = serialize_users(request, followers)
    return JsonResponse(serialized_users, safe=False)


@login_required
def update_blog_url(request):
    profile = request.user.profile
    blog_url = request.POST.get("blog_url", None)
    profile.posts.all().delete()
    if blog_url:
        profile.blog_url = request.POST.get("blog_url", None)
        profile.feed_status = UserProfile.FEED_PROCESSING
        profile.save()
        add_feed_initializer_to_queue(profile)
        return JsonResponse("Success", safe=False)
    else:
        profile.blog_url = ""
        profile.feed_url = ""
        profile.feed_status = UserProfile.NO_BLOG_OR_FEED_URL
        profile.save()
    return JsonResponse("Error", safe=False)


@login_required
def feed_status(request):
    return JsonResponse({"feed_status": request.user.profile.feed_status})


def get_recommended_users_for_topic(topic_slug, excluded_ids):
    users = []
    posts = Post.objects.filter(
        topics__slug=topic_slug, aggregate_votes_count__gte=15
    ).order_by("-updated_on")[:20]
    for post in posts:
        if post.profile.id not in excluded_ids:
            users.append(post.profile)
            excluded_ids.add(post.profile.id)
    if len(users) == 0:
        posts = Post.objects.filter(
            topics__slug=topic_slug, aggregate_votes_count__gte=2
        ).order_by("-updated_on")[:20]
        for post in posts:
            if post.profile.id not in excluded_ids:
                users.append(post.profile)
                excluded_ids.add(post.profile.id)
    if len(users) <= 2:
        users.extend(
            list(
                UserProfile.objects.filter(
                    feed_status=UserProfile.FEED_ACTIVATED,
                    recommended_in__slug=topic_slug,
                )
                .exclude(last_post_date__isnull=True)
                .order_by("-last_post_date")
                .exclude(id__in=list(excluded_ids))
                .distinct()[:10]
            )
        )
    return users


def get_user_suggestions(request):
    excluded_ids = set()
    profile = None
    if request.user.is_authenticated:
        profile = request.user.profile
        excluded_ids.add(profile.id)
        for user in list(profile.following.all()):
            excluded_ids.add(user.id)

    topic_slug = request.GET.get("topic", None)
    selected_users = []
    if not topic_slug:
        selected_users = list(
            UserProfile.objects.exclude(recommended_in__isnull=True)
            .exclude(id__in=list(excluded_ids))
            .exclude(last_post_date__isnull=True)
            .order_by("-last_post_date")
            .distinct()[:40]
        )

        if profile:
            topics = profile.topics.all()
            for topic in topics:
                selected_users.extend(
                    get_recommended_users_for_topic(topic_slug, excluded_ids)
                )
                for selected_user in selected_users:
                    excluded_ids.add(selected_user.id)
    else:
        selected_users.extend(get_recommended_users_for_topic(topic_slug, excluded_ids))

    selected_count = 0
    suggested_users = set()
    limit = request.POST.get("limit", 20)
    cutoff = limit * 50
    i = 0
    while selected_count < min(limit, len(selected_users)):
        random_int = random.randint(0, len(selected_users) - 1)
        user = selected_users[random_int]
        if user not in suggested_users:
            suggested_users.add(user)
            selected_count += 1
        i += 1
        if i > cutoff:
            break

    serialized_users = serialize_users(request, list(suggested_users), True)
    return JsonResponse(serialized_users, safe=False)


def profile_setup_status(request):
    # TODO: Return Queue content length to show a neat progress bar
    return JsonResponse(
        {"fetched_following_users": request.user.profile.fetched_following_users}
    )
