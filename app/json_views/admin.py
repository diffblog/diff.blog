from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from app.models import Vote, Post, Comment, CommentVote


@login_required
def boost(request):
    assert request.user.profile.is_admin
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    post.upvotes_count = post.upvotes_count + 1
    post.save()
    post.update_aggregate_votes_count_and_score()
    return JsonResponse("Success", safe=False)
