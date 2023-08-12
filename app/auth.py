from app.models import UserProfile
from app.queue import (
    add_to_following_users_processor_queue,
    add_to_followers_processor_queue,
    add_to_language_tags_processor_queue,
    add_to_follow_organizations_processor_queue,
)
from feed.github import initialize_following_users


def get_github_info(
    backend, strategy, details, response, user=None, social=None, *args, **kwargs
):
    if backend.name == "github":
        existing_user_profiles = UserProfile.objects.filter(auth=user)

        twitter_username = (response["twitter_username"] or "")[:100]

        if not existing_user_profiles:
            github_id = response["id"]
            access_token = response["access_token"]
            full_name = (response["name"] or "")[:50]
            company = (response["company"] or "")[:100]
            bio = response["bio"]
            location = (response["location"] or "")[:100]
            website_url = (response["blog"] or "")[:100]

            followers_count = response["followers"]
            following_count = response["following"]

            user_profile = UserProfile.objects.filter(github_id=github_id)
            if not user_profile:
                user_profile = UserProfile.objects.create(
                    auth=user,
                    github_username=user.username,
                    github_token=access_token,
                    is_activated=True,
                    full_name=full_name,
                    github_id=github_id,
                    company=company,
                    bio=bio,
                    location=location,
                    website_url=website_url,
                    followers_count=followers_count,
                    following_count=following_count,
                    twitter_username=twitter_username,
                )
            else:
                user_profile = user_profile[0]
                user_profile.auth = user
                user_profile.github_token = access_token
                user_profile.is_activated = True
                user_profile.full_name = full_name
                user_profile.company = company
                user_profile.bio = bio
                user_profile.location = location
                user_profile.website_url = website_url
                user_profile.twitter_username = twitter_username
                user_profile.followers_count = response["followers"]
                user_profile.following_count = response["following"]
                user_profile.save()

            add_to_following_users_processor_queue(user_profile)
            add_to_language_tags_processor_queue(user_profile)
            add_to_follow_organizations_processor_queue(user_profile)
            add_to_followers_processor_queue(user_profile)
        else:
            existing_user_profile = existing_user_profiles[0]

            latest_username_in_github = response["login"]
            if (
                latest_username_in_github
                and existing_user_profile.github_username != latest_username_in_github
            ):
                existing_user_profile.github_username = latest_username_in_github
                existing_user_profile.save(update_fields=["github_username"])

            if (
                twitter_username
                and existing_user_profile.twitter_username != twitter_username
            ):
                existing_user_profile.twitter_username = twitter_username
                existing_user_profile.save(update_fields=["twitter_username"])
