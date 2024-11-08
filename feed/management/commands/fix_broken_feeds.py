from django.core.management.base import BaseCommand
from app.models import Post, UserProfile
from feed.lib import read_feed
from django.utils import timezone
from datetime import timedelta
import feedparser
import feedfinder2  # Importing feedfinder2 for detecting alternative feeds
from urllib.parse import urlparse
import threading

# Define a function to run with a timeout
def find_feeds_with_timeout(search_url, timeout=2):
    result = [None]  # Use a list to hold the result to allow modification in the thread

    # Define a worker function to perform the operation
    def worker():
        try:
            result[0] = feedfinder2.find_feeds(search_url)
        except Exception:
            result[0] = None

    # Create and start the thread
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout)  # Wait for the thread with a timeout

    # Check if the thread is still alive, indicating a timeout occurred
    if thread.is_alive():
        return None  # Timeout, return None or any appropriate fallback
    else:
        return result[0]  # Return the result if operation completes within timeout

class Command(BaseCommand):
    help = "Fixes broken feeds if possible"

    def handle(self, *args, **options):
        one_month_ago = timezone.now() - timedelta(days=30)
        
        inactive_users = UserProfile.objects.filter(last_post_date__lt=one_month_ago).exclude(feed_url="")
        # inactive_users = UserProfile.objects.filter(github_username="ajturner")

        for profile in inactive_users:
            if profile.feed_url:
                feed = read_feed(profile.feed_url)
            
            if feed and feed.entries:
                print(f"User has active feed {profile.github_username}")
                continue

            print(f"No feed valid found for {profile.github_username} with URL {profile.feed_url}")
            try:
                alternative_feeds = find_feeds_with_timeout(profile.feed_url)
            except:
                alternative_feeds = None
            
            if alternative_feeds:
                new_feed_url = alternative_feeds[0]
                if new_feed_url == profile.feed_url:
                    continue

                new_feed = read_feed(new_feed_url)
                if new_feed and new_feed.entries:
                    print(f"\033[92mNew feed founfor user {profile.github_username}: {new_feed_url}\033[0m")
                    profile.feed_url = new_feed_url
                    profile.save()
                    continue

            website_url = profile.website_url
            if website_url:
                profile.feed_url = ""
                profile.save()
            else:
                parsed_url = urlparse(profile.feed_url)
                website_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                print(f"Setting website_url to {website_url}")
                profile.website_url = website_url
                profile.feed_url = ""
                profile.save()
                