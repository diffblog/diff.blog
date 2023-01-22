from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
import json
import urllib

from app.models import Vote, Post, Comment, UserProfile, Topic
from app.json_views.profile import serialize_users
from app.models import slugify, Search
from app.json_views.post import set_user_votes


def get_search_string_from_param(search_param):
    search_string = search_param.replace("+", " ")
    return urllib.parse.unquote(search_string)


def get_user_results(request, search_string):
    users = UserProfile.objects.filter(
        Q(github_username__search=search_string)
        | Q(full_name__search=search_string)
        | Q(bio__search=search_string)
    ).distinct()[:50]
    return serialize_users(request, users, True)


def do_post_search(search_string, limit=50):
    return (
        Post.objects.filter(
            Q(topics__display_name__search=search_string)
            | Q(title__search=search_string)
        )
        .order_by("-updated_on")
        .distinct()[:limit]
    )


def get_post_results(request, search_string):
    posts = []
    serialized_posts = []

    if len(search_string) > 3:
        posts = do_post_search(search_string, 50)

        for post in posts:
            serialized_posts.append(post.serialize())

        set_user_votes(request, serialized_posts)
    return serialized_posts


def do_topic_search(search_string, limit=50):
    return Topic.objects.filter(
        Q(display_name__search=search_string) | Q(slug=search_string)
    ).distinct()[:limit]


def get_topic_results(request, search_string):
    topics = []
    serialized_topics = []

    if len(search_string) > 3:
        topics = do_topic_search(search_string, 50)

        for topic in topics:
            serialized_topics.append(topic.serialize())
    return serialized_topics


def search(request):
    param = request.GET.get("param")
    search_string = get_search_string_from_param(param)
    search_type = request.GET.get("type", None) or "posts"
    if search_type == "users":
        result = {
            "users": get_user_results(request, search_string),
        }
    elif search_type == "posts":
        result = {
            "posts": get_post_results(request, search_string),
        }
    elif search_type == "topics":
        result = {"topics": get_topic_results(request, search_string)}

    Search.objects.create(query=search_string)
    return JsonResponse(result, safe=False)
