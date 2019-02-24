from app.models import UserProfile, Topic
import requests as r
from multiprocessing import Queue, Pool
import time
from diffblog.secrets import github_access_token

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
    response = r.get("https://api.github.com/users/{}".format(user.github_username),headers=headers)
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
    user.blog_url = user_response["blog"]
    user.followers_count = user_response["followers"]
    user.following_count = user_response["following"]
    user.save()

def populate_user_profile_details():
    users = UserProfile.objects.all()
    pool = Pool()
    pool.map(_populate_user_profile_details, users)

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
