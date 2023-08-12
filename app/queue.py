import django_rq

from feed.github import (
    initialize_following_users,
    initialize_followers,
    set_user_language_tags,
    follow_organizations,
)
from feed.lib import initialize_user_feed
from app.plugin import set_post_info

following_bootstrapper = django_rq.get_queue("following_bootstrapper")
followers_bootstrapper = django_rq.get_queue("followers_bootstrapper")
feed_queue = django_rq.get_queue("feed")
language_queue = django_rq.get_queue("language_scanner")
follow_organizations_queue = django_rq.get_queue("follow_organizations")
event_log_processor_queue = django_rq.get_queue("event_log_processor")
set_plugin_post_info_processor_queue = django_rq.get_queue("set_plugin_post_info")


def add_to_following_users_processor_queue(from_user):
    # TODO: Create finisher queues
    following_bootstrapper.enqueue(initialize_following_users, from_user)


def add_to_followers_processor_queue(from_user):
    followers_bootstrapper.enqueue(initialize_followers, from_user)


def add_feed_initializer_to_queue(profile):
    feed_queue.enqueue(initialize_user_feed, profile)


def add_to_language_tags_processor_queue(profile):
    language_queue.enqueue(set_user_language_tags, profile)


def add_to_follow_organizations_processor_queue(profile):
    follow_organizations_queue.enqueue(follow_organizations, profile)


def add_to_set_plugin_post_info_processor_queue(post):
    set_plugin_post_info_processor_queue.enqueue(set_post_info, post)
