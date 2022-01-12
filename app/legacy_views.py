from django.http.response import Http404
from django.shortcuts import render, redirect

from app.models import Post
from app.views import render_post_view


def topic_page(request, topic, feed_type):
    return redirect("/tag/{}/{}/".format(topic, feed_type), permanent=True)


def get_post_legacy(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404()
    if post.title:
        return redirect("/post/" + post.slug, permanent=True)
    return render_post_view(request, post)
