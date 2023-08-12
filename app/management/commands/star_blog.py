from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post, GitHubCampaign

from feed.github import diffblog_headers
import requests
import feedparser

import json

from feed.github import get_rss_feed_url_from_blog_url, feed_has_valid_english_posts

ISSUE_CREATION_ENABLED = False


def star_repo(github_username, repo_name):
    if GitHubCampaign.objects.filter(
        github_username__iexact=github_username,
        status=GitHubCampaign.STAR_REPO,
        repo_name=repo_name,
    ).count():
        print("🤹 Repo already starred {}. Skipping".format(github_username))
        return

    url = "https://api.github.com/user/starred/{}/{}".format(github_username, repo_name)
    print("Starring repo")

    response = requests.put(url, headers=diffblog_headers)

    if response.status_code in [200, 201, 204]:
        GitHubCampaign.objects.create(
            github_username=github_username,
            repo_name=repo_name,
            status=GitHubCampaign.STAR_REPO,
        )
        return True
    return False


class Command(BaseCommand):
    help = "Star blogs of GitHub users"

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

            feed_url = get_rss_feed_url_from_blog_url(repo_name)

            if not feed_url:
                print("❌📰 No RSS feed found for ", repo_name)
                continue

            if not feed_has_valid_english_posts(feed_url):
                print("❌🏴󠁧󠁢󠁥󠁮󠁧󠁿 No valid posts found for ", repo_name)

            count += 1
            print("✅ Valid blog found for", github_username, repo_name)

            star_repo(github_username=github_username, repo_name=repo_name)

        print(
            "Found {count} valid blogs out of {total_count}".format(
                count=count, total_count=len(repos)
            )
        )
