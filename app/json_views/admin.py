from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

from app.models import Vote, Post, Comment, CommentVote

def boost(request):
    assert(request.user.profile.is_admin)
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    post.upvotes_count = post.upvotes_count + 1
    post.save()
    post.update_score()
    return JsonResponse("Success", safe=False)
