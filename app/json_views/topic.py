from django.http import JsonResponse
from django.http import QueryDict
from django.contrib.auth.decorators import login_required

import json
import logging

from app.models import Topic
from app.queue import add_feed_initializer_to_queue
from app.topic import get_popular_topics

logger = logging.getLogger(__name__)


@login_required
def topics(request):
    profile = request.user.profile
    if request.method == "POST":
        topic_ids = json.loads(request.POST.get("topic_ids", ""))
        topics = []
        for topic_id in topic_ids:
            topic = Topic.objects.get(id=topic_id)
            profile.topics.add(topic)
            topics.append(topic)
        profile.save()
        return JsonResponse("Success", safe=False)
    elif request.method == "GET":
        topics = [topic.serialize() for topic in profile.topics.all().order_by("slug")]
        return JsonResponse(topics, safe=False)
    elif request.method == "DELETE":
        data = QueryDict(request.body)
        topic_id = data.get("topic_id")
        topic = Topic.objects.get(id=topic_id)
        profile.topics.remove(topic)
        profile.save()
        return JsonResponse("Success", safe=False)


def popular_topics(request):
    topics = get_popular_topics()
    topics_serialized = [topic.serialize() for topic in topics]
    return JsonResponse(topics_serialized, safe=False)
