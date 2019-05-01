from django.core.management.base import BaseCommand, CommandError

from feed.github import populate_user_model_feed_urls_from_google

class Command(BaseCommand):
    help = 'Fetches the top users from GitHub'

    def handle(self, *args, **options):
        populate_user_model_feed_urls_from_google()
