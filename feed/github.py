from app.models import UserProfile, Topic, Category
import requests as r
from multiprocessing import Queue, Pool
import time
from diffblog.secrets import diffblog_github_access_token
from feedfinder2 import find_feeds
from googlesearch import search
from django.db import connection
import feedparser
from polyglot.detect import Detector

from feed.blogs import recommended_blog_list

diffblog_headers = {"Authorization": "token {}".format(diffblog_github_access_token)}

blog_item = """
"{}": [
    "{}",
    [
        "{}"
    ]
],
"""


def _populate_user_profile_details(user):
    if user.github_id:
        return
    print("Populating user profile of ", user.github_username)
    response = r.get(
        "https://api.github.com/users/{}".format(user.github_username),
        headers=diffblog_headers,
    )
    if response.status_code != 200:
        print(user.github_username)
        print("Unxpected status code ", response.status_code)
        print(response.content)
        return
    user_response = response.json()
    user.full_name = (user_response["name"] or "")[:50]
    user.github_id = user_response["id"]
    user.company = (user_response["company"] or "")[:100]
    user.bio = user_response["bio"] or ""
    user.location = (user_response["location"] or "")[:100]
    user.website_url = (user_response["blog"] or "")[:100]
    user.followers_count = user_response["followers"]
    user.following_count = user_response["following"]
    user.save()


def populate_user_profile_details_parallel():
    users = UserProfile.objects.all()
    pool = Pool()
    connection.close()
    pool.map(_populate_user_profile_details, users)


def populate_user_profile_details_serial():
    users = UserProfile.objects.all()
    for user in users:
        _populate_user_profile_details(user)


def get_rss_feed_url_from_blog_url(blog_url):
    feed_urls = find_feeds(blog_url)
    if len(feed_urls) == 0:
        return False
    return feed_urls[0]


def feed_has_valid_english_posts(feed_url):
    blog_feed = feedparser.parse(feed_url)
    if len(blog_feed.entries) == 0:
        return False

    for entry in blog_feed.entries:
        from feed.lib import get_valid_english_summary

        if get_valid_english_summary(entry, feed_url):
            return True

    return False


def _populate_user_model_feed_urls_from_google(username, language=None):
    if username in recommended_blog_list:
        return

    response = r.get(
        "https://api.github.com/users/{}".format(username), headers=headers
    ).json()
    try:
        blog_url = response["blog"]
    except:
        print(response)
        print(response.content)
        return

    if blog_url:
        feed_url = get_rss_feed_url_from_blog_url(blog_url)
        if feed_url:
            if language is None:
                language_map = {}
                set_language_tags_from_own_repos(username, language_map)
                language_map = sort_map_desc(language_map)
                language = language_map[0][0]
            print(blog_item.format(username, feed_url, language))
            return

    return

    for url in search("{} {} blog".format(response["name"], username), stop=1):
        if "github.com" in url:
            continue
        if "twitter.com" in url:
            continue
        if "linkedin.com" in url:
            continue
        if "facebook.com" in url:
            continue
        feeds = find_feeds(url)
        if len(feeds) == 0:
            continue
        print('("{}", "{}"),'.format(username, feed_urls[0]))
        break


def get_most_followed_users(language, limit=10):
    users = []
    for i in range(0, limit):
        if language:
            url = "https://api.github.com/search/users?&q=followers:>=600+language:{}&order=desc&per_page=100&page={}".format(
                language, str(i)
            )
        else:
            url = "https://api.github.com/search/users?&q=followers:>=600&order=desc&per_page=100&page={}".format(
                str(i)
            )

        response = r.get(url, headers=headers).json()
        items = response["items"]
        for item in items:
            users.append(item["login"])
            print(item["login"])
    pool = Pool()
    pool.map(_populate_user_model_feed_urls_from_google, users)
    # for user in users:
    #    _populate_user_model_feed_urls_from_google(user)


def initialize_following_users(user, limit=1, start=0):
    headers = {"Authorization": "token {}".format(user.github_token)}
    i = start
    while True:
        if i >= limit:
            break
        url = "https://api.github.com/users/{}/following?page={}&per_page=100".format(
            user.github_username, str(i)
        )
        try:
            response = r.get(url, headers=headers)
            i += 1
            following = response.json()
            if len(following) == 0:
                break
            for item in following:
                following_user, created = UserProfile.objects.get_or_create(
                    github_username=item["login"], github_id=item["id"]
                )
                user.following.add(following_user)
        except Exception:
            pass
    user.fetched_following_users = True
    user.save()


def initialize_followers(from_user, limit=1, start=0):
    headers = {"Authorization": "token {}".format(from_user.github_token)}
    i = start
    while True:
        if i >= limit:
            break
        url = "https://api.github.com/users/{}/followers?page={}&per_page=100".format(
            from_user.github_username, str(i)
        )
        response = r.get(url, headers=headers)
        i += 1
        following = response.json()
        if len(following) == 0:
            break
        for item in following:
            to_user, created = UserProfile.objects.get_or_create(
                github_username=item["login"], github_id=item["id"]
            )
            to_user.following.add(from_user)


def create_social_graph(initial_user):
    q = Queue()
    processed = set()
    q.put(initial_user)
    while q:
        username = q.get()
        if username in processed:
            continue
        processed.add(username)

        response = r.get("https://api.github.com/users/{}/followers".format(username))
        followers = response.json()
        if len(followers) < 30:
            time.sleep(2)
            continue
        time.sleep(2)

        print("# ", username)
        i = 0
        while True:
            response = r.get(
                "https://api.github.com/users/{}/following?page={}".format(
                    username, str(i)
                )
            )
            i += 1
            following = response.json()
            if len(following) == 0:
                break
            for user in following:
                q.put(user["login"])
                print("-", user["login"])
            time.sleep(2)
        time.sleep(5)


def sort_map_desc(input_map):
    import operator

    return sorted(input_map.items(), key=operator.itemgetter(1), reverse=True)


def set_language_tags_from_own_repos(github_username, language_map):
    url = "https://api.github.com/users/{}/repos?per_page=50".format(github_username)
    response = r.get(url, headers=headers)
    repos = response.json()
    for repo in repos:
        language = repo["language"]
        if language:
            if language in language_map:
                language_map[language] += 1
            else:
                language_map[language] = 1


def set_user_language_tags(user):
    language_category = Category.objects.get(name="Language")
    headers = {"Authorization": "token {}".format(user.github_token)}

    language_map = {}
    set_language_tags_from_own_repos(user.github_username, language_map)

    url = "https://api.github.com/users/{}/starred?per_page=50".format(
        user.github_username
    )
    response = r.get(url, headers=headers)
    repos = response.json()
    for repo in repos:
        language = repo["language"]
        if language:
            if language in language_map:
                language_map[language] += 1
            else:
                language_map[language] = 1

    language_map = sort_map_desc(language_map)
    for language_tuple in language_map[:5]:
        language = language_tuple[0]
        topic, _ = Topic.objects.get_or_create(
            display_name=language, category=language_category
        )
        user.topics.add(topic)


def follow_organizations(user):
    url = "https://api.github.com/users/{}/orgs".format(user.github_username)
    response = r.get(url, headers=headers)
    organizations = response.json()
    for organization_dict in organizations:
        organization_id = organization_dict["id"]
        organization_username = organization_dict["login"]
        organization, _ = UserProfile.objects.get_or_create(
            github_username=organization_username,
            github_id=organization_id,
            is_organization=True,
        )
        user.following.add(organization)
