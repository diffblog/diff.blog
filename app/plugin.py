from django.utils.timezone import now
from newspaper import Article

from app.models import Post
from mirrors.lib import sync_mirror_upvotes


def create_base_post_object(link, profile):
    return Post.objects.create(
        link=link, profile=profile, updated_on=now(), source=Post.PLUGIN
    )


def set_post_info(post):
    article = Article(url=post.link)
    article.download()
    article.parse()
    if article.text:
        post.content = article.text
    if article.publish_date:
        post.updated_on = article.publish_date
    post.summary = article.text
    sync_mirror_upvotes([post])
