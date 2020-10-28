from django.core.management.base import BaseCommand, CommandError

from feed.github import get_most_followed_users


class Command(BaseCommand):
    help = "Fetches the top users from GitHub"

    def add_arguments(self, parser):
        parser.add_argument("--language", action="store", default=None)

    def handle(self, *args, **options):
        get_most_followed_users(options["language"])
