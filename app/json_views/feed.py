from django.shortcuts import render
from django.http import JsonResponse

from app.models import Vote, Post, Comment
import random

def get_new_posts(request):
    latest_id = request.GET.get("latest_id", None)
    if latest_id is not None:
        posts = Post.objects.filter(id__lte = latest_id).order_by('-id')[:30]
    else:
        posts = Post.objects.filter().order_by('-id')[:30]

    posts = [post.serialize() for post in posts]

    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(profile=request.user.profile).values_list("post__id", flat=True)
    else:
        user_votes = []

    for post in posts:
        if post["id"] in user_votes:
            post["upvoted"] = True
        else:
            post["upvoted"] = False
    return JsonResponse(posts, safe=False)

def get_following_posts(request):
    latest_id = request.GET.get("latest_id", None)
    if latest_id is not None:
        posts = Post.objects.filter(id__lte = latest_id, profile__in=request.user.profile.following.all()).order_by('-updated_on')[:30]
    else:
        posts = Post.objects.filter(profile__in=request.user.profile.following.all()).order_by('-updated_on')[:30]

    posts = [post.serialize() for post in posts]

    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(profile=request.user.profile).values_list("post__id", flat=True)
    else:
        user_votes = []

    for post in posts:
        if post["id"] in user_votes:
            post["upvoted"] = True
        else:
            post["upvoted"] = False
    return JsonResponse(posts, safe=False)

def get_user_votes(request):
    votes = Vote.objects.filter(profile=request.user.profile)
    return JsonResponse([{"post_id": votes.post.id for vote in votes}], safe=False)

def vote(request):
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    try:
        vote = Vote.objects.get(post=post, profile=request.user.profile)
        vote.delete()
        post.upvotes_count = post.upvotes_count - 1
        post.save()
    except Vote.DoesNotExist:
        Vote.objects.create(post=post, profile=request.user.profile)
        post.upvotes_count = post.upvotes_count + 1
        post.save()
    return JsonResponse("Success", safe=False)

def comment(request):
    content = request.POST.get("content")
    post = Post.objects.get(id=request.POST.get("post_id"))
    post.comments_count += 1
    post.save(update_fields=["comments_count"])
    Comment.objects.create(content=content, profile=request.user.profile, post=post)
    return JsonResponse("Success", safe=False)

def get_comments(request):
    post_id = request.GET.get("post_id")
    comments = Comment.objects.filter(post__id=post_id)
    comments = [comment.serialize() for comment in comments]
    return JsonResponse(comments, safe=False)
