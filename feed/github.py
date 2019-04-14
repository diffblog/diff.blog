from app.models import UserProfile, Topic, Category
import requests as r
from multiprocessing import Queue, Pool
import time
from diffblog.secrets import github_access_token
from feedfinder2 import find_feeds
from googlesearch import search 
from django.db import connection

headers = {'Authorization': 'token {}'.format(github_access_token)}

def initialize_top_users():
    topics = Topic.objects.all()

    for topic in topics:
        url = "https://api.github.com/search/users?&q=followers:>=600+language:{}&order=desc".format(topic.display_name)
        response = r.get(url, headers=headers).json()
        items = response["items"]
        for item in items:
            user, created = UserProfile.objects.get_or_create(github_id=item["id"], github_username=item["login"])
            user.topics.add(topic)
            user.save()
        time.sleep(2)

def _populate_user_profile_details(user):
    response = r.get("https://api.github.com/users/{}".format(user.github_username), headers=headers)
    if response.status_code != 200:
        print(user.github_username)
        print("Unxpected status code ", response.status_code)
        print(response.content)
        return
    user_response = response.json()
    user.full_name = (user_response["name"] or "")[:50]
    user.github_id = user_response["id"]
    user.company = (user_response["company"] or "")[:50]
    user.bio = (user_response["bio"] or "")[:100]
    user.location = (user_response["location"] or "")[:50]
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

def _populate_user_model_feed_urls_from_google(user):
    if user.blog_url_type:
        return
    print(user.full_name)
    if user.website_url:
        feed_urls = find_feeds(user.website_url)
        if len(feed_urls) != 0:
            user.feed_url = feed_urls[0]
            user.blog_url_type = UserProfile.FROM_GITHUB
            user.save()
            return

    for url in search("{} blog".format(user.full_name, user.github_username), stop=1):
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
        user.feed_url = feeds[0]
        user.blog_url_type = UserProfile.FROM_GOOGLE
        user.save()
        print(user.feed_url)
        break

def populate_user_model_feed_urls_from_google():
    users = UserProfile.objects.all()
    pool = Pool()
    pool.map(_populate_user_model_feed_urls_from_google, users)
    #for user in users:
    #    _populate_user_model_feed_urls_from_google(user)

def initialize_following_users(user, limit=1, start=0):
    headers = {'Authorization': 'token {}'.format(user.github_token)}
    i = start
    while True:
        if i >= limit:
            break
        url = "https://api.github.com/users/{}/following?page={}&per_page=100".format(user.github_username, str(i))
        try:
            response = r.get(url, headers=headers)
            i += 1
            following = response.json()
            if len(following) == 0:
                break
            for item in following:
                following_user, created = UserProfile.objects.get_or_create(github_username=item["login"], github_id=item["id"])
                user.following.add(following_user)
        except Exception:
            pass
    user.fetched_following_users = True
    user.save()

def initialize_followers(from_user, limit=1, start=0):
    headers = {'Authorization': 'token {}'.format(from_user.github_token)}
    i = start
    while True:
        if i >= limit:
            break
        url = "https://api.github.com/users/{}/followers?page={}&per_page=100".format(from_user.github_username, str(i))
        response = r.get(url, headers=headers)
        i += 1
        following = response.json()
        if len(following) == 0:
            break
        for item in following:
            to_user, created = UserProfile.objects.get_or_create(github_username=item["login"], github_id=item["id"])
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
            response = r.get("https://api.github.com/users/{}/following?page={}".format(username, str(i)))
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

def set_user_language_tags(user):
    language_category = Category.objects.get(name="Language")
    headers = {'Authorization': 'token {}'.format(user.github_token)}

    language_map = {}

    url = "https://api.github.com/users/{}/repos?per_page=50".format(user.github_username)
    response = r.get(url, headers=headers)
    repos = response.json()
    for repo in repos:
        language = repo["language"]
        if language:
            if language in language_map:
                language_map[language] += 1
            else:
                language_map[language] = 1

    if len(repos) < 20:
        url = "https://api.github.com/users/{}/starred?per_page=50".format(user.github_username)
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
        topic, _ = Topic.objects.get_or_create(display_name=language, category=language_category)
        user.topics.add(topic)

def follow_organizations(user):
    url = "https://api.github.com/users/{}/orgs".format(user.github_username)
    response = r.get(url, headers=headers)
    organizations = response.json()
    for organization_dict in organizations:
        organization_id = organization_dict["id"]
        organization_username = organization_dict["login"]
        organization, _ = UserProfile.objects.get_or_create(github_username=organization_username,
                                                            github_id=organization_id,
                                                            is_organization=True)
        user.following.add(organization)
