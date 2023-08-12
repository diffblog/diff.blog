import feedparser
from dateutil import parser as date_parser
from datetime import datetime, timedelta
from multiprocessing import Pool
from datetime import date
from django.utils.text import slugify
from django.utils.timezone import now
from django.db.models import Avg
import random
from feedfinder2 import find_feeds
import requests as requests
from django.db import connection
from bs4 import BeautifulSoup
import logging
from django.db.models import Q
from django.db.utils import DataError
import io
from newspaper import Article

from app.models import UserProfile, Post, Topic, Category
from feed.github import (
    populate_user_profile_details_parallel,
    populate_user_profile_details_serial,
)
from feed.blogs import recommended_blog_list
from feed.blacklist import users as blacklisted_users
from app.lib import normalize_link, save_to_pocket

# Get an instance of a logger
logger = logging.getLogger(__name__)

domain_topics = [
    "Decentralized Web",
    "App Development",
    "Startups",
    "Open Source",
    "Networking",
    "Engineering Team Blogs",
    "Computer Science Theory",
    "Distributed Systems",
    "Machine Learning",
    "Programming Languages",
    "Cryptocurrency",
    "System Programming",
    "Hardware",
    "Web Development",
    "Cybersecurity",
    "Reverse Engineering",
    "Game Development",
    "Design",
    "Data Science",
    "Simulation",
    "Virtual Reality",
    "Travel",
    "Music",
]


def initialize_tables():
    initialize_topics()
    initialize_reccomended_users()
    populate_user_profile_details_parallel()
    set_users_feed_url_from_blog_url()
    fetch_all_blogs_posts()


def update_recommended_blog_list(populate_github_details=True):
    initialize_topics()
    initialize_reccomended_users()
    if populate_github_details:
        populate_user_profile_details_serial()
    set_users_feed_url_from_blog_url()


def initialize_topics():
    domain_category, _ = Category.objects.get_or_create(name="Domain")
    for topic in domain_topics:
        Topic.objects.get_or_create(display_name=topic, category=domain_category)


def initialize_reccomended_users():
    for username in recommended_blog_list:
        user, _ = UserProfile.objects.get_or_create(github_username=username)
        blog_dict = recommended_blog_list[username]
        blog_url = blog_dict[0]
        topics = blog_dict[1]
        user.blog_url = blog_url

        for topic_name in topics:
            if topic_name in domain_topics:
                category, _ = Category.objects.get_or_create(name="Domain")
            else:
                category, _ = Category.objects.get_or_create(name="Language")
            topic, _ = Topic.objects.get_or_create(
                display_name=topic_name, category=category
            )
            user.topics.add(topic)
            topic.recommended.add(user)

        user.save()


def random_date():
    start_date = date.today().replace(day=1, month=1, year=2016).toordinal()
    end_date = date.today().toordinal()
    return date.fromordinal(random.randint(start_date, end_date))


def initialize_user_feed(profile):
    update_feed_url(profile)
    fetch_posts(profile)


def update_feed_url(user):
    if not user.blog_url:
        return

    feed_urls = find_feeds(user.blog_url)
    if len(feed_urls) != 0:
        user.feed_url = feed_urls[0]
        user.save()
    else:
        user.feed_url = ""
        user.feed_status = UserProfile.FEED_NOT_FOUND
    user.save()


def _set_feed_url_from_blog_url(user):
    if user.blog_url and not user.feed_url:
        print("Trying to fetch the feed url of ", user.github_username)
        try:
            feed_urls = find_feeds(user.blog_url)
        except Exception:
            feed_urls = []
            print("Exception while parsing ", user.blog_url)
        if len(feed_urls) != 0:
            user.feed_url = feed_urls[0]
            user.blog_url_type = UserProfile.HANDPICKED
            user.save()


def set_users_feed_url_from_blog_url():
    users = UserProfile.objects.all()
    connection.close()
    pool = Pool()
    pool.map(_set_feed_url_from_blog_url, users)


def get_valid_english_summary(entry, feed_url):
    content = None
    if "content" in entry:
        content = entry["content"]
        try:
            content = content[0]["value"]
            if "medium.com" in feed_url and len(content) < 1000:
                return False
        except:
            print("Invalid content for ", feed_url)

    if "summary" in entry:
        summary = entry["summary"]
    elif "description" in entry:
        summary = entry["description"]
    elif content is not None:
        summary = content
        logger.warning("Summary missing for", feed_url)
    else:
        logger.warning("Content not found for", feed_url)
        return None

    soup = BeautifulSoup(summary)
    summary = soup.get_text().replace("\n", " ")

    # try:
    #     language = Detector(summary).languages[0]
    #     if language.code != "en":
    #         logger.warning("Non english language", feed_url)
    #         return None
    # except polyglot.detect.base.UnknownLanguage:
    #     logger.warning("Unknown language for summary", feed_url)
    #     return summary
    # except pycld2.error:
    #     logger.warning("pycld2.error while analyzing language", feed_url)
    # except:
    #     logger.warning("Unknown exception while analyzing language for")
    #     return summary
    return summary


def fetch_cover_photo(post):
    article = Article(url=post.link)
    article.download()
    article.parse()

    cover_photo = ""
    if article.top_image:
        cover_photo = article.top_image

    if "favicon" in cover_photo:
        for photo in article.imgs:
            if "favicon" not in photo:
                cover_photo = photo
                break

    if cover_photo:
        post.cover_photo_url = cover_photo
        post.save(update_fields=["cover_photo_url"])


def read_feed(feed_url):
    try:
        resp = requests.get(
            feed_url, timeout=20.0, headers={"User-Agent": "https://diff.blog"}
        )
    except requests.exceptions.ConnectTimeout:
        return
    except requests.exceptions.ConnectionError:
        return
    except requests.exceptions.SSLError:
        return
    except requests.ReadTimeout:
        return

    content = io.BytesIO(resp.content)
    return feedparser.parse(content)


def fetch_posts(user):
    if user.github_username in blacklisted_users:
        return

    feed_url = user.feed_url
    blog_feed = read_feed(feed_url)

    if blog_feed is None:
        return

    if len(blog_feed.entries) == 0:
        user.feed_status = UserProfile.FEED_POSTS_NOT_FOUND
        user.save()
        return

    for entry in blog_feed.entries:
        # TODO: Make the check more robust
        keys = set(entry.keys())

        if not set(["content", "summary", "description"]).intersection(keys):
            continue

        if "title" not in keys:
            continue

        if "link" not in keys:
            continue

        title = entry["title"][:200]
        link = entry["link"]

        if len(link) > 300 or len(link) <= 2:
            # Likely some kind of spam/ad.
            continue

        new_post_count = 0
        post = Post.objects.filter(Q(title=title) | Q(link=link), profile=user)
        if not post:
            if "published" in entry:
                try:
                    date_parsed = date_parser.parse(entry["published"])
                except ValueError:
                    logger.warning("Error while parsing published of", feed_url)
                    continue
            elif "pubDate" in entry:
                try:
                    date_parsed = date_parser.parse(entry["pubDate"])
                except ValueError:
                    logger.warning("Error while parsing pubDate of ", feed_url)
                    continue
            elif "updated" in entry:
                try:
                    date_parsed = date_parser.parse(entry["updated"])
                except ValueError:
                    logger.warning("Error while parsing updated of ", feed_url)
                    continue
            else:
                logger.warning("Date no found while parsing ", feed_url)
                # TODO: Make this random but preserving the order
                date_parsed = random_date()
                # For now
                continue

            summary = get_valid_english_summary(entry, feed_url)
            if not summary:
                continue

            try:
                seconds_since_posted = (now() - date_parsed).total_seconds()
            except TypeError:
                # timezone not aware
                seconds_since_posted = (datetime.now() - date_parsed).total_seconds()

            # Some of the blog posts often have a time older than the
            # time it was published. If the difference is less than 24 hours
            # we should set the time of the post to current time so that
            # its ranking is not affected because of the old time.
            if seconds_since_posted < 24 * 60 * 60 or seconds_since_posted < 0:
                date_parsed = now()
                new_post_count += 1

                if new_post_count >= 3:
                    date_parsed = now() - timedelta(days=new_post_count)

            post = Post(
                title=title,
                link=entry["link"],
                profile=user,
                summary=summary,
                updated_on=date_parsed,
                source=Post.RSS_FEED,
                normalized_link=normalize_link(link),
            )

            post.upvotes_count = 1
            post.save()

            fetch_cover_photo(post)

            if not user.last_post_date or user.last_post_date < post.updated_on:
                user.last_post_date = post.updated_on
                user.save()

            post.update_aggregate_votes_count_and_score()

            category, _ = Category.objects.get_or_create(name="Raw")
            if "tags" in entry:
                for tag in entry["tags"]:
                    try:
                        topic = Topic.objects.filter(slug=slugify(tag["term"]))
                        if not topic:
                            topic = Topic.objects.create(
                                display_name=tag["term"], category=category
                            )
                            topic.category = category
                            topic.save()
                        else:
                            topic = topic[0]
                        post.topics.add(topic)
                        if topic.updated_on < now():
                            topic.updated_on = now()
                            topic.save()
                    except DataError:
                        logger.warning("Topic too large ", tag["term"], entry["link"])

            run_integrations(post)

    if user.feed_status != UserProfile.FEED_ACTIVATED:
        user.feed_status = UserProfile.FEED_ACTIVATED
    user.save()


def fetch_all_blogs_posts():
    pool = Pool()
    users = UserProfile.objects.all()
    connection.close()
    pool.map(fetch_posts, users)


def update_aggregate_votes_count_and_score_of_posts():
    posts = Post.objects.all()
    for post in posts:
        post.update_aggregate_votes_count_and_score()


def run_integrations(post):
    posted_by = post.profile
    followers = posted_by.followers.all()
    for follower in followers:
        if follower.pocket_auto_save and follower.pocket_api_key is not None:
            save_to_pocket(follower, post)
