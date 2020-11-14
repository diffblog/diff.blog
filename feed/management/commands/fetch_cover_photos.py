from django.core.management.base import BaseCommand, CommandError

from app.models import Post
from feed.lib import fetch_posts, fetch_cover_photo


class Command(BaseCommand):
    help = "Fetches the new posts of users from RSS feed and save in DB"

    def add_arguments(self, parser):
        parser.add_argument("--username", action="store", default=None)
        parser.add_argument("--limit", action="store", default=50)

    def handle(self, *args, **options):
        username = options["username"]
        limit = options["limit"]
        if options["username"] is None:
            posts = Post.objects.filter().order_by("-updated_on")[:limit]
        else:
            posts = Post.objects.filter(profile__github_username=username)[:limit]

        for post in posts:
            print("Updating ", post.link)
            try:
                fetch_cover_photo(post)
            except Exception:
                print("Error")
