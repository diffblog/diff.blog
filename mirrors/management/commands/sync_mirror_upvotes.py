import json
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

from diffblog.secrets import (
    reddit_consumer_key,
    reddit_consumer_secret,
    reddit_username,
    reddit_password,
)
from app.models import MirrorSource, MirrorPost, Post

from datetime import timedelta
from django.utils import timezone

from mirrors.lib import sync_mirror_upvotes

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch votes from HN, Reddit etc"

    def handle(self, *args, **options):
        three_days_back = timezone.now() - timedelta(days=3)
        posts = Post.objects.filter(updated_on__gte=three_days_back)
        sync_mirror_upvotes(posts)
