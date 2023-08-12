from django.core.management.base import BaseCommand, CommandError

from app.models import UserProfile
from feed.lib import fetch_posts


class Command(BaseCommand):
    help = "Fetches the new posts of users from RSS feed and save in DB"

    def add_arguments(self, parser):
        parser.add_argument("--username", action="store", default=None)

    def handle(self, *args, **options):
        username = options["username"]
        if options["username"] is None:
            users = UserProfile.objects.all()
        else:
            user = UserProfile.objects.get(github_username=username)
            users = [user]
        for user in users:
            if user.feed_url:
                print(user.full_name)
                try:
                    fetch_posts(user)
                except Exception as e:
                    message = "{} while fetching feed for {}".format(
                        str(e), user.github_username
                    )
                    # TODO: Add email notification
