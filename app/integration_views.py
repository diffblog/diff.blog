from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from app.models import Post, UserProfile, Topic, Category, Vote, BlogSuggestion
from feed.lib import update_feed_url, fetch_posts
from app.queue import add_feed_initializer_to_queue
from diffblog.secrets import pocket_consumer_key
import random
import json

from pocket import Pocket

redirect_uri = "https://diff.blog/integrations/auth/pocket/finish"


@login_required
def pocket_start_auth(request):
    request_token = Pocket.get_request_token(
        consumer_key=pocket_consumer_key, redirect_uri=redirect_uri
    )
    request.session["request_token"] = request_token
    auth_url = Pocket.get_auth_url(code=request_token, redirect_uri=redirect_uri)
    return HttpResponseRedirect(auth_url)


@login_required
def pocket_finish_auth(request):
    profile = request.user.profile
    request_token = request.session.get("request_token", None)
    user_credentials = Pocket.get_credentials(
        consumer_key=pocket_consumer_key, code=request_token
    )
    access_token = user_credentials["access_token"]
    profile.pocket_api_key = access_token
    profile.save()
    return HttpResponseRedirect("/account/settings/integrations/")
