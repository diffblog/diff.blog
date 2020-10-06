from django.shortcuts import render, redirect

from app.models import Post

def topic_page(request, topic, feed_type):
    return redirect("/tag/{}/{}/".format(topic, feed_type), permanent=True)

def get_post_legacy(request, post_id):
    post = Post.objects.get(id=post_id)
    return redirect("/post/" + post.slug, permanent=True)
