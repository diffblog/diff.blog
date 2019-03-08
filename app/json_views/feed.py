from django.shortcuts import render
from django.http import JsonResponse
from dateutil.parser import parse as iso_date_parser

from app.models import Vote, Post, Comment, CommentVote
import random

def get_posts(request, feed_type):
    if feed_type == "new":
        last_post_date = request.GET.get("last_post_updated_on", None)
        if last_post_date is not None:
            last_post_date = iso_date_parser(last_post_date)
            posts = Post.objects.filter(updated_on__lte = last_post_date).order_by('-updated_on')[:30]
        else:
            posts = Post.objects.filter().order_by('-updated_on')[:30]

    if feed_type == "following":
        last_post_date = request.GET.get("last_post_updated_on", None)
        if last_post_date is not None:
            last_post_date = iso_date_parser(last_post_date)
            posts = Post.objects.filter(updated_on__lte = last_post_date, profile__in=request.user.profile.following.all()).order_by('-updated_on')[:30]
        else:
            posts = Post.objects.filter(profile__in=request.user.profile.following.all()).order_by('-updated_on')[:30]

    if feed_type == "top":
        last_post_score = request.GET.get("last_post_score", None)
        if last_post_score is not None:
            posts = Post.objects.filter(score__lte=last_post_score).order_by('-score')[:30]
        else:
            posts = Post.objects.filter().order_by('-score')[:30]

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
        post.update_score()
    except Vote.DoesNotExist:
        Vote.objects.create(post=post, profile=request.user.profile)
        post.upvotes_count = post.upvotes_count + 1
        post.save()
        post.update_score()
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
    serialized_comments = [comment.serialize() for comment in comments]

    if request.user.is_authenticated:
        user_votes = CommentVote.objects.filter(profile=request.user.profile, comment__in=comments).values_list("comment__id", flat=True)
    else:
        user_votes = []

    for comment in serialized_comments:
        if comment["id"] in user_votes:
            comment["upvoted"] = True
        else:
            comment["upvoted"] = False

    return JsonResponse(serialized_comments, safe=False)
