from django.shortcuts import render
from django.http import JsonResponse
from dateutil.parser import parse as iso_date_parser
from django.contrib.auth.decorators import login_required

from app.models import CommentVote, Comment, Post
from app.lib import save_to_pocket

def pocket_add(request):
    if not request.user.profile.pocket_api_key:
        return JsonResponse({'status':'false','message':'authorize pocket'}, status=400)
    post = Post.objects.get(id=request.POST.get("post_id"))
    save_to_pocket(user, post)
    return JsonResponse("Success", safe=False)
