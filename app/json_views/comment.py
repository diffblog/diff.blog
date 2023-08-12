from django.shortcuts import render
from django.http import JsonResponse
from dateutil.parser import parse as iso_date_parser
from django.contrib.auth.decorators import login_required

from app.models import CommentVote, Comment, Post


@login_required
def create_comment(request):
    content = request.POST.get("content")
    post = Post.objects.get(id=request.POST.get("post_id"))
    post.comments_count += 1
    post.save(update_fields=["comments_count"])
    comment = Comment.objects.create(
        content=content, profile=request.user.profile, post=post
    )
    return JsonResponse("Success", safe=False)


def get_comments(request):
    post_id = request.GET.get("post_id")
    comments = Comment.objects.filter(post__id=post_id)
    serialized_comments = [comment.serialize() for comment in comments]

    if request.user.is_authenticated:
        user_votes = CommentVote.objects.filter(
            profile=request.user.profile, comment__in=comments
        ).values_list("comment__id", flat=True)
    else:
        user_votes = []

    for comment in serialized_comments:
        if comment["id"] in user_votes:
            comment["upvoted"] = True
        else:
            comment["upvoted"] = False

    return JsonResponse(serialized_comments, safe=False)


@login_required
def vote_comment(request):
    comment_id = request.POST.get("comment_id")
    comment = Comment.objects.get(id=comment_id)
    try:
        vote = CommentVote.objects.get(comment=comment, profile=request.user.profile)
        vote.delete()
        comment.upvotes_count = comment.upvotes_count - 1
        comment.save()
    except CommentVote.DoesNotExist:
        CommentVote.objects.create(comment=comment, profile=request.user.profile)
        comment.upvotes_count = comment.upvotes_count + 1
        comment.save()
    return JsonResponse("Success", safe=False)
