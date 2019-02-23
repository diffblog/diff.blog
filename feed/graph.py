from app.models import UserProfile, Topic
import requests as r
from multiprocessing import Queue
import time

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
