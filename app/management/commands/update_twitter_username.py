from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, Topic, Category
from diffblog.secrets import diffblog_github_access_token
import requests as r

diffblog_headers = {"Authorization": "token {}".format(diffblog_github_access_token)}


def get_user_profile_details(user):
    response = r.get(
        "https://api.github.com/users/{}".format(user.github_username),
        headers=diffblog_headers,
    )
    print(user.github_username)
    if response.status_code != 200:
        print("Unxpected status code ", response.status_code)
        print(response.content)
        return
    user_response = response.json()
    user.twitter_username = user_response.get("twitter_username", "") or ""
    if user.twitter_username:
        print("✅")
    else:
        print("❌")
    user.save(update_fields=["twitter_username"])


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        users = UserProfile.objects.filter(twitter_username=None)

        for user in users:
            get_user_profile_details(user)
