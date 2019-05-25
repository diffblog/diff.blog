from django.shortcuts import render
from django.http import JsonResponse
from dateutil.parser import parse as iso_date_parser
from django.contrib.auth.decorators import login_required

from app.models import CommentVote, Comment, Post
from diffblog.secrets import pocket_consumer_key

import pocket

def pocket_add(request):
    access_token = request.user.profile.pocket_api_key
    if not access_token:
        return JsonResponse({'status':'false','message':'authorize pocket'}, status=400)

    pocket_instance = pocket.Pocket(pocket_consumer_key, access_token)
    post = Post.objects.get(id=request.POST.get("post_id"))
    pocket_instance.add(url=post.link, title=post.title)
    return JsonResponse("Success", safe=False)
