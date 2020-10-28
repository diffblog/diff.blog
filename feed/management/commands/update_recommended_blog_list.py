from django.core.management.base import BaseCommand, CommandError

from feed.lib import update_recommended_blog_list


class Command(BaseCommand):
    help = "Fetches the top users from GitHub"

    def handle(self, *args, **options):
        update_recommended_blog_list()
