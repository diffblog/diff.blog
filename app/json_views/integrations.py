from django.shortcuts import render
from django.http import JsonResponse
from dateutil.parser import parse as iso_date_parser
from django.contrib.auth.decorators import login_required

from app.models import CommentVote, Comment, Post
from app.lib import save_to_pocket
from app.queue import add_to_event_log_processor_queue


def pocket_add(request):
    if not request.user.profile.pocket_api_key:
        return JsonResponse(
            {"status": "false", "message": "authorize pocket"}, status=400
        )
    post = Post.objects.get(id=request.POST.get("post_id"))
    save_to_pocket(request.user.profile, post)
    add_to_event_log_processor_queue(request.user.profile, "save_to_pocket", post)
    return JsonResponse("Success", safe=False)
