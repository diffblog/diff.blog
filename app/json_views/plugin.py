from app.lib import normalize_link
from django.http import JsonResponse
from django.db.models import Q

from app.models import MirrorPost, Post, UserProfile
from app.queue import add_to_set_plugin_post_info_processor_queue
from app.plugin import create_base_post_object
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_post_info(request):
    encoded_blog_post_url = request.POST.get("encoded_blog_post_url")
    plugin_public_api_key = request.POST.get("plugin_public_api_key")

    url = encoded_blog_post_url.replace("%3A", ":").replace("%2F", "/")

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
