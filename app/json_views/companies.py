from django.http import JsonResponse

from app.models import UserProfile, Post
from .profile import serialize_users


def companies_by_topic(request):
    topic_slug = request.GET.get("topic", None)
    user_ids = (
        Post.objects.filter(topics__slug=topic_slug)
        .values_list("profile", flat=True)
        .distinct()
    )
    users = UserProfile.objects.filter(
        id__in=list(user_ids), is_organization=True
    ).order_by("-followers_count")
    return JsonResponse(serialize_users(request, users), safe=False)
