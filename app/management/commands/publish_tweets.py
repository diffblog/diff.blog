import time

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post, Tweet
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core import mail
from django.urls import reverse


from diffblog.secrets import (
    twitter_api_keys,
    twitter_api_secret_keys,
    twitter_access_tokens,
    twitter_access_token_secrets,
)

import tweepy


tweet_template = """
{post_title}{post_author_twitter_username}
{topics_string}

{post_link}
"""


class Command(BaseCommand):
    help = "Publish the most popular post to Twitter"

    def add_arguments(self, parser):
        parser.add_argument("--twitter-account", action="store", default=None)

    def get_tags_as_string_from_post(self, post, twitter_account):
        hashtags = []
        if twitter_account == "ThePythonDaily":
            hashtags = ["python", "pythonnews", "pythondaily"]
        if twitter_account == "TheJavascriptDaly":
            hashtags = ["javascript", "javascriptnews", "javascriptdaily"]

        for topic in post.topics.all():
            hashtag = topic.slug.replace("-", "")
            if hashtag not in hashtags:
                hashtags.append(hashtag)

        string = ""
        for hashtag in hashtags[:6]:
            string += "#{} ".format(hashtag)
        return string

    def get_post_to_publish(self, twitter_account):
        if twitter_account == "diffblog":
            time_cutoff = timezone.now() - timedelta(days=3)
            posts = Post.objects.filter(updated_on__gte=time_cutoff).order_by(
                "-aggregate_votes_count"
            )[:100]
            for post in posts:
                if Tweet.objects.filter(
                    post=post, posted_from=twitter_account
                ).exists():
                    continue
                if post.aggregate_votes_count < 15 and not post.profile.is_activated:
                    continue
                if post.aggregate_votes_count < 5:
                    return None
                return post

        if twitter_account == "ThePythonDaily":
            time_cutoff = timezone.now() - timedelta(days=7)
            posts = (
                Post.objects.filter(
                    Q(topics__display_name__search="python") | Q(title__search="python")
                )
                .filter(updated_on__gte=time_cutoff)
                .order_by("-aggregate_votes_count")
            )
            for post in posts:
                if Tweet.objects.filter(
                    post=post, posted_from=twitter_account
                ).exists():
                    continue
                return post

        if twitter_account == "TheJavascriptDaly":
            time_cutoff = timezone.now() - timedelta(days=7)
            posts = (
                Post.objects.filter(
                    Q(topics__display_name__search="javascript")
                    | Q(title__search="javascript")
                )
                .filter(updated_on__gte=time_cutoff)
                .order_by("-aggregate_votes_count")
            )
            for post in posts:
                if Tweet.objects.filter(
                    post=post, posted_from=twitter_account
                ).exists():
                    continue
                return post

    def publish_tweets_for_twitter_account(self, twitter_account):
        auth = tweepy.OAuthHandler(
            twitter_api_keys[twitter_account], twitter_api_secret_keys[twitter_account]
        )
        auth.set_access_token(
            twitter_access_tokens[twitter_account],
            twitter_access_token_secrets[twitter_account],
        )
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        timeline = api.home_timeline()

        post = self.get_post_to_publish(twitter_account)
        if post is None:
            return

        post_author_twitter_username = ""
        if post.profile.twitter_username:
            post_author_twitter_username = " (@" + post.profile.twitter_username + ")"

        content = tweet_template.format(
            post_title=post.title,
            post_link=post.link,
            post_author_twitter_username=post_author_twitter_username,
            topics_string=self.get_tags_as_string_from_post(post, twitter_account),
        )
        response = api.update_status(content)
        Tweet.objects.create(
            tweet_id=response.id, post=post, posted_from=twitter_account
        )

    def handle(self, *args, **options):
        if options["twitter_account"] is None:
            twitter_accounts = ["diffblog", "ThePythonDaily", "TheJavascriptDaly"]
        else:
            twitter_accounts = [options["twitter_account"]]

        for twitter_account in twitter_accounts:
            self.publish_tweets_for_twitter_account(twitter_account)
