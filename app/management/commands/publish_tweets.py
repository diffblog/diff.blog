import time

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post
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


class Command(BaseCommand):
    help = "Publish the most popular post to Twitter"

    def add_arguments(self, parser):
        # parser.add_argument("--username", action="store", default=None)
        pass

    def handle(self, *args, **options):
        pass
