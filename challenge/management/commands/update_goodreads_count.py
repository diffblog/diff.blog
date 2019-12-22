from django.core.management.base import BaseCommand, CommandError

from challenge.models import Count, LastId

import feedparser

class Command(BaseCommand):
    help = 'Updates the Goodreads count'

    def handle(self, *args, **kwargs):
        feed = feedparser.parse('https://www.goodreads.com/user/updates_rss/43580070')
        last_id_object = LastId.objects.last()

        if last_id_object is not None:
            last_response_id = last_id_object.response_id
        else:
            last_response_id = None

        for entry in feed.entries:
            response_id = entry['id']
            if response_id == last_response_id:
                break

            title = entry['title']

            update_count = False
            if "Vishnu\n      is" in title:
                update_count = True
            
            if "Vishnu is currently reading" in title:
                update_count = True

            if update_count:
                Count.objects.create(type=Count.BOOKS, value=1)
                LastId.objects.create(type=Count.BOOKS, response_id=response_id)
                break
