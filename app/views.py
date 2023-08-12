from app.topic import get_popular_topics
from feed.github import _populate_user_profile_details
from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from app.models import (
    Post,
    UserProfile,
    Topic,
    Category,
    Vote,
    BlogSuggestion,
    UserList,
    get_topic,
)
from feed.lib import _set_feed_url_from_blog_url, update_feed_url, fetch_posts
from app.digest import (
    get_global_popular_posts_from_last_week,
    get_popular_posts_from_following_users_last_week,
    get_weekly_digest_posts,
)
from diffblog.secrets import plugin_marketing_page_api_key
from django.views.decorators.clickjacking import xframe_options_exempt

import random
import json
import urllib
import markdown


def home(request, slug=None, feed_type=None, landing_page=False):
    topic = Topic.objects.filter(slug=slug).first()
    topic_display_name = ""
    topic_id = ""
    if topic is not None:
        topic_display_name = topic.display_name
        topic_id = topic.id

    pocket_show_button = json.dumps(True)
    if request.user.is_authenticated:
        pocket_show_button = json.dumps(request.user.profile.pocket_show_button)
        auth_username = request.user.profile.github_username
    else:
        auth_username = "unauthenticated_user"

    return render(
        request,
        "home.html",
        context={
            "auth_username": auth_username,
            "js_pocket_show_button": pocket_show_button,
            "topic_id": topic_id,
            "topic_display_name": topic_display_name,
            "slug": slug,
            "feed_type": feed_type,
            "landing_page": landing_page,
        },
    )


@login_required
def select_topics(request):
    topics = get_popular_topics()
    context = {"topics": topics[:30]}
    return render(request, "signup_finish.html", context=context)


def profile_page(request, username, page_type="posts"):
    is_me = False
    is_following = False
    is_logged_in = request.user.is_authenticated
    pocket_show_button = json.dumps(True)

    try:
        profile = UserProfile.objects.get(github_username__iexact=username)
        if is_logged_in:
            pocket_show_button = json.dumps(request.user.profile.pocket_show_button)
            if profile == request.user.profile:
                is_me = True
            else:
                is_following = profile in request.user.profile.following.all()
        else:
            is_following = False
            is_me = False
        # TODO: Create a function to get these values and cache it
        posts_count = Post.objects.filter(profile=profile).count()
        votes_count = Vote.objects.filter(profile=profile).count()
        following_count = profile.following.all().count()
        followers_count = profile.followers.all().count()
        is_recommended = profile.recommended_in.all().count() != 0
    except UserProfile.DoesNotExist:
        raise Http404()

    template = "profile_{}.html".format(page_type)

    return render(
        request,
        template,
        {
            "profile": profile,
            "type": page_type,
            "is_me": is_me,
            "js_is_me": json.dumps(is_me),
            "js_is_following": json.dumps(is_following),
            "posts_count": posts_count,
            "votes_count": votes_count,
            "following_count": following_count,
            "followers_count": followers_count,
            "is_recommended": is_recommended,
            "js_pocket_show_button": pocket_show_button,
        },
    )


def render_post_view(request, post):
    following = json.dumps(False)
    upvoted = False

    if request.user.is_authenticated:
        profile = request.user.profile
        following = json.dumps(post.profile in profile.following.all())
        upvoted = Vote.objects.filter(profile=profile, post=post).exists()

    featured_on = post.mirror_posts.all().order_by("-votes")
    return render(
        request,
        "post.html",
        context={
            "post": post,
            "user": request.user,
            "following": following,
            "upvoted": upvoted,
            "featured_on": featured_on,
            "domain": urlparse(post.link).netloc,
        },
    )


def get_post(request, post_slug):
    try:
        post = Post.objects.get(slug=post_slug)
    except Post.DoesNotExist:
        raise Http404()
    return render_post_view(request, post)


def users(request):
    users = UserProfile.objects.all()
    return render(request, "users.html", context={"users": users})


@login_required
def profile_settings(request):
    context = {}
    profile = request.user.profile

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", "")
        profile.bio = request.POST.get("bio", "")
        profile.save()
        context["message"] = "Profile updated"

    context["type"] = "profile"
    context["profile"] = profile
    return render(request, "profile_settings.html", context=context)


@login_required
def blog_settings(request):
    profile = request.user.profile
    context = {
        "type": "blog",
        "blog_url": profile.blog_url or "",
        "feed_status": profile.feed_status,
    }

    return render(request, "blog_settings.html", context=context)


@login_required
def integrations_settings(request):
    profile = request.user.profile

    context = {
        "type": "integrations",
        "profile": profile,
    }

    if request.method == "POST":
        integration = request.POST.get("integration", "")
        if integration == "email":
            profile.send_weekly_digest_email = (
                request.POST.get("send_weekly_digest_email") == "on"
            )
            profile.save()

        if integration == "pocket":
            profile.pocket_show_button = request.POST.get("pocket_show_button") == "on"
            profile.pocket_auto_save = request.POST.get("pocket_auto_save") == "on"
            profile.save()

    if (
        profile.pocket_auto_save or profile.pocket_show_button
    ) and not profile.pocket_api_key:
        context["error"] = "Please link your Pocket"

    return render(request, "settings_integrations.html", context=context)


def user_suggestions_page(request, slug=""):
    topic = None
    if slug:
        topic = get_topic(slug)
    return render(request, "user_suggestions.html", {"topic": topic})


def companies_by_topic(request, slug=""):
    topic = None
    if slug:
        topic = get_topic(slug)
    return render(request, "companies_by_topic.html", {"topic": topic})


def search_results(request, query=""):
    search_type = request.GET.get("type", "posts")

    if query:
        search_query = query
    else:
        search_query = request.GET.get("s", "")

    search_param = search_query.replace(" ", "+")
    return render(
        request,
        "search_results.html",
        {
            "search_type": search_type,
            "search_query": search_query,
            "search_param": search_param,
        },
    )


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


def suggest(request):
    username = ""
    if request.method == "POST":
        suggested_username = request.POST.get("username", None)
        suggested_url = request.POST.get("url", None)

        if request.user.is_authenticated and request.user.is_staff:
            assert suggested_username is not None
            profile, created = UserProfile.objects.get_or_create(
                github_username=suggested_username
            )
            if created:
                _populate_user_profile_details(profile)
            profile.blog_url = suggested_url
            profile.save()
            _set_feed_url_from_blog_url(profile)
        else:
            suggestion = BlogSuggestion.objects.create(
                username=suggested_username, url=suggested_url
            )
            profile = None
            if request.user.is_authenticated:
                profile = request.user.profile
                suggestion.suggested_by = profile
                suggestion.save()

    elif request.method == "GET":
        username = request.GET.get("username", "")

    return render(
        request,
        "suggest.html",
        context={"show_confirmation": request.method == "POST", "username": username},
    )


def faq(request):
    return render(request, "faq.html")


def curated_lists_page(request, slug):
    user_list = UserList.objects.get(slug=slug)
    users = user_list.users.all()
    if request.user.is_authenticated:
        my_profile = request.user.profile
        following = my_profile.following.all()
    else:
        my_profile = None
        following = None

    return render(
        request,
        "user_lists.html",
        context={
            "user_list": user_list,
            "users": users,
            "my_profile": my_profile,
            "following": following,
        },
    )


@login_required
def weekly_digest(request):
    global_posts, following_posts, job_postings = get_weekly_digest_posts(
        request.user.profile
    )
    return render(
        request,
        "emails/compiled/digest.html",
        context={
            "global_posts": global_posts,
            "following_posts": following_posts,
            "job_postings": job_postings,
        },
    )


def unsubscribe_from_emails(request, key):
    try:
        user = UserProfile.objects.get(unsubscribe_key=key)
    except:
        return HttpResponse("Invalid link")
    if request.method == "POST":
        user.unsubscribe_from_all_emails()
    return render(request, "unsubscribe.html", {"user": user})


def plugin_page(request):
    if request.user.is_authenticated:
        user_plugin_public_api_key = request.user.profile.plugin_public_api_key
        code_snippet = """
<script id="diffblog-plugin-script" async="false" src="https://diff.blog/static/js/diffblog_plugin_v1.js"></script> 
<script>
        document.getElementById("diffblog-plugin-script").addEventListener("load", function () {{
            DiffBlog(
                "{user_plugin_public_api_key}"
            );
        }});
</script>
    """.format(
            user_plugin_public_api_key=user_plugin_public_api_key
        )
        profile = request.user.profile
    else:
        code_snippet = "Please login to generate the code."
        user_plugin_public_api_key = ""
        profile = None

    return render(
        request,
        "plugin_marketing_page_v1.html",
        {
            "code_snippet": code_snippet,
            "plugin_public_api_key": user_plugin_public_api_key,
            "plugin_marketing_page_api_key": plugin_marketing_page_api_key,
        },
    )


@xframe_options_exempt
def plugin_iframe(request):
    return render(
        request,
        "plugin_iframe.html",
        context={
            "plugin_public_api_key": request.GET.get("plugin_public_api_key", ""),
            "url_encoded_blog_post_url": request.GET.get(
                "url_encoded_blog_post_url", ""
            ),
        },
    )
