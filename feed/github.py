from app.models import UserProfile, Topic
import requests as r
from multiprocessing import Queue, Pool
import time
from diffblog.secrets import github_access_token
from feedfinder2 import find_feeds
from googlesearch import search 

headers = {'Authorization': 'token {}'.format(github_access_token)}

def initialize_top_users():
    topics = Topic.objects.all()

    for topic in topics:
        url = "https://api.github.com/search/users?&q=followers:>=600+language:{}&order=desc".format(topic.name)
        response = r.get(url).json()
        items = response["items"]
        for item in items:
            user, created = UserProfile.objects.get_or_create(github_id=item["id"], github_username=item["login"])
            user.topics.add(topic)
            user.save()
        time.sleep(2)

def _populate_user_profile_details(user):
    response = r.get("https://api.github.com/users/{}".format(user.github_username), headers=headers)
    if response.status_code != 200:
        print("Unxpected status code ", response.status_code)
        print(response.content)
        return
    user_response = response.json()
    if user_response["name"]:
        user.full_name = user_response["name"]
    user.company = user_response["company"]
    user.bio = user_response["bio"]
    user.location = user_response["location"]
    user.website_url = user_response["blog"]
    user.followers_count = user_response["followers"]
    user.following_count = user_response["following"]
    user.save()

def populate_user_profile_details(search_google=False):
    users = UserProfile.objects.all()
    pool = Pool()
    pool.map(_populate_user_profile_details, users)

def _populate_user_model_feed_urls(user):
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

def populate_user_model_feed_urls():
    users = UserProfile.objects.all()
    pool = Pool()
    pool.map(_populate_user_model_feed_urls, users)
    #for user in users:
    #    _populate_user_model_feed_urls(user)

def initialize_following_users(from_user):
    headers = {'Authorization': 'token {}'.format(from_user.github_token)}
    i = 1
    while True:
        if i == 20:
            break
        url = "https://api.github.com/users/{}/following?page={}".format(from_user.github_username, str(i))
        response = r.get(url, headers=headers)
        i += 1
        following = response.json()
        if len(following) == 0:
            break
        for item in following:
            to_user, created = UserProfile.objects.get_or_create(github_username=item["login"], github_id=item["id"])
            from_user.following.add(to_user)

def initialize_followers(from_user):
    headers = {'Authorization': 'token {}'.format(from_user.github_token)}
    i = 1
    while True:
        if i == 20:
            break
        url = "https://api.github.com/users/{}/followers?page={}".format(from_user.github_username, str(i))
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
