from app.lib import normalize_link
from django.http import JsonResponse
from django.db.models import Q

from app.models import MirrorPost, Post, UserProfile
from app.queue import add_to_set_plugin_post_info_processor_queue
from app.plugin import create_base_post_object


def get_post_info(request):
    url = request.GET.get("url")
    plugin_public_api_key = request.GET.get("plugin_public_api_key")

    try:
        profile = UserProfile.objects.get(plugin_public_api_key=plugin_public_api_key)
    except UserProfile.DoesNotExist:
        return JsonResponse("Invalid API key", safe=False)

    post = Post.objects.filter(
        Q(link=url) | Q(normalized_link=normalize_link(url)), profile=profile
    ).last()
    if post:
        mirror_posts = [
            mirror_post.serialize()
            for mirror_post in MirrorPost.objects.filter(post=post)
        ]
        data = {
            "diffblog_url": post.uri,
            "diffblog_aggregate_votes_count": post.aggregate_votes_count,
            "mirror_posts": mirror_posts,
        }
    else:
        post = create_base_post_object(url, profile)
        data = {
            "diffblog_url": post.uri,
            "diffblog_aggregate_votes_count": post.aggregate_votes_count,
            "mirror_posts": [],
        }
        add_to_set_plugin_post_info_processor_queue(post)
    return JsonResponse(data, safe=False)
