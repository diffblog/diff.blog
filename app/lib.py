import pocket
import random
import string
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

from diffblog.secrets import pocket_consumer_key


def get_random_lowercase_string(length):
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


def save_to_pocket(profile, post):
    pocket_instance = pocket.Pocket(pocket_consumer_key, profile.pocket_api_key)
    pocket_instance.add(url=post.link, title=post.title)


def remove_param(url, param):
    """
    Remove a parameter from a url.
    """
    u = urlparse(url)
    query = parse_qs(u.query, keep_blank_values=True)
    query.pop(param, None)
    u = u._replace(query=urlencode(query, True))
    return urlunparse(u)


def normalize_link(link):
    """
    Normalize the URL so that we can use it as an ID for searching through it.
    """
    if link.startswith("http://"):
        link = link[7:]
    if link.startswith("https://"):
        link = link[8:]
    if "source" in link:
        link = remove_param(link, "source")
    if link.endswith("/"):
        link = link[:-1]
    return link
