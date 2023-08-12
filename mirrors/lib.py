import json
import logging
from datetime import datetime
from dateutil import parser as date_parser

from django.core.cache import cache
from app.lib import normalize_link

from diffblog.secrets import (
    reddit_consumer_key,
    reddit_consumer_secret,
    reddit_username,
    reddit_password,
)
from app.models import MirrorSource, MirrorPost, Post

from datetime import timedelta
from django.utils import timezone

import furl
import requests
import requests.auth

logger = logging.getLogger(__name__)


def obtain_reddit_access_token():
    client_auth = requests.auth.HTTPBasicAuth(
        reddit_consumer_key, reddit_consumer_secret
    )
    post_data = {
        "grant_type": "password",
        "username": reddit_username,
        "password": reddit_password,
    }
    headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=client_auth,
        data=post_data,
        headers=headers,
    )
    return response.json()["access_token"]


def get_actual_link(link):
    try:
        response = requests.get(link)
        if len(response.history) != 0:
            link = response.url
    except:
        # Drew Devault had a weird lik
        # gemini://drewdevault.com/gemini/2020/09/27/Gemini-and-Hugo.gmi
        pass
    return furl.furl(link).remove(args=True, fragment=True).url


def process_reddit_upvotes(token, post):
    actual_link = get_actual_link(post.link)
    headers = {
        "Authorization": "bearer {}".format(token),
        "User-Agent": "ChangeMeClient/0.1 by YourUsername",
    }
    response = requests.get(
        "https://oauth.reddit.com/api/info.json?url={}".format(actual_link),
        headers=headers,
    )
    response_json = response.json()

    for submission in response_json["data"]["children"]:
        data = submission["data"]
        if (
            "ups" not in data
            or "subreddit_name_prefixed" not in data
            or "permalink" not in data
        ):
            logger.warning("Skipping fetching votes from Reddit")
            continue

        if normalize_link(post.link) != normalize_link(data["url"]):
            continue

        upvotes = data["ups"]
        subreddit = data["subreddit_name_prefixed"]
        permalink = data["permalink"]
        url = "https://reddit.com/{}".format(permalink)
        source, _ = MirrorSource.objects.get_or_create(name=subreddit)
        mirror_post, created = MirrorPost.objects.get_or_create(
            post=post, source=source
        )
        if created or mirror_post.votes < upvotes:
            mirror_post.votes = upvotes
            mirror_post.url = url
            mirror_post.created_on = datetime.utcfromtimestamp(data["created_utc"])
            mirror_post.save(update_fields=["votes", "url", "created_on"])
            post.update_aggregate_votes_count_and_score()


def process_hn_upvotes(post):
    actual_link = get_actual_link(post.link)
    response = requests.get(
        "https://hn.algolia.com/api/v1/search?query={}".format(actual_link)
    )
    data = json.loads(response.content)
    source, _ = MirrorSource.objects.get_or_create(name="Hacker News")

    for hit in data["hits"]:
        if hit["points"] is None or hit["url"] is None or hit["objectID"] is None:
            logger.warning("Skipping fetching votes from HN")
            continue

        if normalize_link(post.link) != normalize_link(hit["url"]):
            continue

        points = hit["points"]
        post_id = hit["objectID"]
        url = "https://news.ycombinator.com/item?id={}".format(post_id)
        mirror_post, created = MirrorPost.objects.get_or_create(
            post=post, source=source
        )
        if created or mirror_post.votes < points:
            mirror_post.votes = points
            mirror_post.url = url
            mirror_post.created_on = date_parser.parse(hit["created_at"])
            mirror_post.save(update_fields=["votes", "url", "created_on"])
            post.update_aggregate_votes_count_and_score()


def sync_mirror_upvotes(posts):
    reddit_access_token = obtain_reddit_access_token()
    for post in posts:
        try:
            process_hn_upvotes(post)
            process_reddit_upvotes(reddit_access_token, post)
        except Exception as e:
            # TODO: notify through email
            pass
    cache.delete("top")
