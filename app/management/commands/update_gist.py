from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post

from diffblog.secrets import diffblog_github_access_token

import requests as r
import json

headers = {"Authorization": "token {}".format(diffblog_github_access_token)}


class Command(BaseCommand):
    help = "Update slugs of all existing posts"

    def handle(self, *args, **options):
        latest_posts = (
            Post.objects.filter()
            .order_by("-score")
            .filter(aggregate_votes_count__gte=50)[:20]
        )

        gist_md = """

## Posts on diff.blog

|User|Title|Points|
|----|-----|---------|
"""

        row_md = '|<img height="24" src="https://avatars.githubusercontent.com/{username}?s=460"> <a href="https://github.com/{username}">{username}</a>|<a href="{post_url}">{title}</a>|<a href="https://diff.blog/{post_id}">{points}</a>|\n'
        for post in latest_posts:
            gist_md += row_md.format(
                profile_id=post.profile.id,
                username=post.profile.github_username,
                title=post.title,
                points=post.aggregate_votes_count,
                post_url=post.link,
                post_id=post.id,
            )

        data = {
            "files": {
                "popular-posts.md": {
                    "filename": "popular-posts.md",
                    "content": gist_md,
                }
            }
        }

        data = {
            "message": "Update posts",
            "committer": {
                "name": "diff.blog",
                "email": "no-reply@diff.blog",
            },
            "content": "",
        }

        data = json.dumps(data)
        response = r.patch(
            "https://api.github.com/repos/diffblog/diffblog/README.md",
            headers=headers,
            data=data,
        )
