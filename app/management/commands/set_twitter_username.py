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


class Command(BaseCommand):
    help = "Set the Twitter username of diff.blog profiles"

    def handle(self, *args, **options):
        for profile in (
            UserProfile.objects.filter(
                Q(twitter_username__isnull=True) | Q(twitter_username__exact="")
            )
            .exclude(followers_count=None)
            .order_by("-followers_count")
        ):
            print("https://github.com/" + profile.github_username)
            print("❔ Is the Twitter username?")
            print("https://twitter.com/" + profile.github_username)
            print("")
            user_input = input("(Y/N): ")
            if user_input.lower() == "y":
                profile.twitter_username = profile.github_username
                profile.save()
                print("🎉 Saved")
            else:
                print("⌨ Enter the twitter username")
                username = input("Twitter username: ")
                if username:
                    profile.twitter_username = username
                    profile.save()
                    print("🎉 Saved")
                else:
                    print("Skipping")
            print()
