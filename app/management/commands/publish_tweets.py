import time

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post, Tweet
from app.digest import get_posts_for_weekly_digest
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core import mail
from django.urls import reverse


from diffblog.secrets import (
    twitter_api_key,
    twitter_api_secret_key,
    twitter_access_token,
    twitter_access_token_secret,
)

import tweepy

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret_key)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

timeline = api.home_timeline()

tweet_template = """
{post_title}{twitter_username}
{post_link}
"""


class Command(BaseCommand):
    help = "Publish the most popular post to Twitter"

    def handle(self, *args, **options):
        time_cutoff = timezone.now() - timedelta(days=3)
        posts = Post.objects.filter(updated_on__gte=time_cutoff).order_by(
            "-aggregate_votes_count"
        )[:100]

        for post in posts:
            if post.tweets.all().exists():
                continue

            if post.aggregate_votes_count < 30 and not post.profile.is_activated:
                continue

            if post.aggregate_votes_count < 5:
                break

            twitter_username = ""
            if post.profile.twitter_username:
                twitter_username = " (@" + post.profile.twitter_username + ")"

            content = tweet_template.format(post_title=post.title, post_link=post.link, twitter_username=twitter_username)
            response = api.update_status(content)
            Tweet.objects.create(tweet_id=response.id_str, post=post)
            break
