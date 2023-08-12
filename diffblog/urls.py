import json
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.contrib.sitemaps import views as sitemaps_views

from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

import app
import app.integration_views
import app.legacy_views
import app.sitemap_classes
import app.views

import app.json_views
import app.json_views.admin
import app.json_views.comment
import app.json_views.integrations
import app.json_views.plugin
import app.json_views.post
import app.json_views.profile
import app.json_views.topic
import app.json_views.search
import app.json_views.companies

import jobs
import jobs.views
import jobs.json_views

urlpatterns = [
    path("", app.views.home, {"feed_type": "top", "landing_page": True}),
    path("recommended/", app.views.home, {"feed_type": "recommended"}),
    path("new/", app.views.home, {"feed_type": "new"}),
    path("following/", app.views.home, {"feed_type": "following"}),
    path("tag/<slug>/top/", app.views.home, {"feed_type": "top"}),
    path("tag/<slug>/new/", app.views.home, {"feed_type": "new"}),
    path("tag/<slug>/following/", app.views.home, {"feed_type": "following"}),
    path("tag/<slug>/users/", app.views.user_suggestions_page),
    path("companies/companies-using-<slug>/", app.views.companies_by_topic),
    path("users/recommended/", app.views.user_suggestions_page),
    path("top/<topic>/", app.legacy_views.topic_page, {"feed_type": "top"}),
    path("new/<topic>/", app.legacy_views.topic_page, {"feed_type": "new"}),
    path("following/<topic>/", app.legacy_views.topic_page, {"feed_type": "following"}),
    path("search/", app.views.search_results),
    path("search/<query>", app.views.search_results),
    path("admin/", admin.site.urls),
    path("", include("social_django.urls")),
    path("signup/topics/", app.views.select_topics),
    path("account/settings/profile/", app.views.profile_settings),
    path("account/settings/blog/", app.views.blog_settings),
    path("account/settings/integrations/", app.views.integrations_settings),
    path("post/<int:post_id>/", app.legacy_views.get_post_legacy),
    path("post/<slug:post_slug>/", app.views.get_post),
    path("lists/<slug>/", app.views.curated_lists_page),
    path("jobs/", jobs.views.jobs_directory),
    path("jobs-in-<location_slug>/", jobs.views.jobs_directory),
    path("<title_slug>-jobs/", jobs.views.jobs_directory),
    path("<title_slug>-jobs-in-<location_slug>/", jobs.views.jobs_directory),
    path("jobs/new/", jobs.views.job_form),
    path("jobs/<location_slug>/", jobs.views.jobs_directory),
    path("logout/", app.views.logout_user),
    path(
        "unsubscribe/emails/<key>/",
        app.views.unsubscribe_from_emails,
        name="unsubscribe_from_emails",
    ),
    path("suggest/", app.views.suggest),
    path("FAQ/", app.views.faq),
    path("django-rq/", include("django_rq.urls")),
    path(
        "sitemap.xml/",
        cache_page(60 * 60)(sitemaps_views.index),
        {"sitemaps": app.sitemap_classes.sitemaps, "sitemap_url_name": "sitemaps"},
    ),
    path(
        "sitemap-<section>.xml/",
        cache_page(60 * 60)(sitemaps_views.sitemap),
        {"sitemaps": app.sitemap_classes.sitemaps},
        name="sitemaps",
    ),
    path(
        "robots.txt/",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("plugin/", app.views.plugin_page, name="plugin_page"),
    path("plugin/iframe", app.views.plugin_iframe, name="plugin_iframe"),
]

if settings.DEVELOPMENT:
    urlpatterns += (path("users", app.views.users),)
    urlpatterns += (path("emails/weekly", app.views.weekly_digest),)


urlpatterns += [
    path("integrations/auth/pocket/start", app.integration_views.pocket_start_auth),
    path("integrations/auth/pocket/finish", app.integration_views.pocket_finish_auth),
]

urlpatterns += [
    path("api/posts/<feed_type>", app.json_views.post.get_posts),
    path("api/user/votes", app.json_views.post.get_user_votes),
    path("api/post/vote", app.json_views.post.upvote_or_downvote_post),
    path("api/user/profile_setup_status", app.json_views.profile.profile_setup_status),
    path("api/user/update_blog_url", app.json_views.profile.update_blog_url),
    path("api/user/feed_status", app.json_views.profile.feed_status),
    path("api/comment/vote", app.json_views.comment.vote_comment),
    path("api/post/comment", app.json_views.comment.create_comment),
    path("api/post/comments", app.json_views.comment.get_comments),
    path("api/user/following", app.json_views.profile.following_users),
    path("api/user/followers", app.json_views.profile.follower_users),
    path("api/user/topics", app.json_views.topic.topics),
    path("api/topics/popular", app.json_views.topic.popular_topics),
    path("api/users/suggestions", app.json_views.profile.get_user_suggestions),
    path("api/search", app.json_views.search.search),
    path("api/admin/boost", app.json_views.admin.boost),
    path("api/integrations/pocket/add", app.json_views.integrations.pocket_add),
    path("api/companies", app.json_views.companies.companies_by_topic),
    path("api/jobs/", jobs.json_views.jobs),
    path("api/plugin/post_info", app.json_views.plugin.get_post_info),
]

urlpatterns += [
    path("<username>/", app.views.profile_page),
    path("<username>/<page_type>/", app.views.profile_page),
]
