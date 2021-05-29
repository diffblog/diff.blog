from django.core.management.base import BaseCommand, CommandError
from requests.api import request
from app.models import Topic, UserProfile, UserList, Post, GitHubCampaign
from app.queue import add_to_event_log_processor_queue

from feed.github import diffblog_headers
import requests
import feedparser
from feedfinder2 import find_feeds

import json

from feed.github import get_rss_feed_url_from_blog_url, feed_has_valid_english_posts

diffblog_headers = {
    "Authorization": "token {}".format("***REMOVED***")
}


class Command(BaseCommand):
    help = "Update slugs of all existing posts"

    def get_email_from_repo(self, github_username, repo):
        response = requests.get(
            "https://api.github.com/repos/{github_username}/{repo}/commits?author=github_username",
            headers=diffblog_headers,
        )
        import pdb

        pdb.set_trace()

    def get_final_url_after_redirect(self, repo_name):
        github_page_url = "https://" + repo_name
        return requests.get(github_page_url).url

    def handle(self, *args, **options):
        response = requests.get(
            "https://api.github.com/search/repositories?q=github.io&sort=updated&order=desc",
            headers=diffblog_headers,
        )
        repos = response.json()["items"]
        count = 0

        for repo in repos:
            github_username = repo["owner"]["login"]
            repo_name = repo["name"]

            if repo["owner"]["type"] != "User":
                print("Skipping {}/{}. Not a user.".format(github_username, repo_name))
                continue

            if UserProfile.objects.filter(
                github_username__iexact=github_username, is_activated=True
            ).count():
                print(
                    "⛷ {} already has a diff.blog account. Skipping.".format(
                        github_username
                    )
                )
                continue

            if GitHubCampaign.objects.filter(
                github_username__iexact=github_username
            ).count():
                print(
                    "🤹 Issue already created for {}. Skipping".format(github_username)
                )
                continue

            blog_url = self.get_final_url_after_redirect(repo_name)
            feed_url = get_rss_feed_url_from_blog_url(blog_url)

            if feed_url:
                if feed_has_valid_english_posts(feed_url):
                    print("✅ Valid blog found for", blog_url)
                    email = self.get_email_from_repo(github_username, repo_name)
                    GitHubCampaign.objects.create(
                        github_username=github_username,
                        repo_name=repo_name,
                        blog_url=blog_url,
                        status=GitHubCampaign.WAITING_FOR_EMAIL_APPROVAL,
                    )
                    print("Added blog for approval")
                    add_to_event_log_processor_queue(
                        None,
                        "create_github_issue",
                        repo_url="https://github.com/{}/{}/".format(
                            github_username, repo_name
                        ),
                    )
                    count += 1
                else:
                    print("❌🏴󠁧󠁢󠁥󠁮󠁧󠁿 No valid posts found for ", repo_name)
            else:
                print("❌📰 No RSS feed found for ", repo_name)

        print(
            "Found {count} valid blogs out of {total_count}".format(
                count=count, total_count=len(repos)
            )
        )
