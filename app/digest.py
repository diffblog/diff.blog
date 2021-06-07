from app.models import Post
from jobs.models import Job
from django.utils import timezone
from datetime import timedelta

cutoff_days = 7


def get_global_popular_posts_from_last_week(ignore_post_ids):
    time_cutoff = timezone.now() - timedelta(days=cutoff_days)
    all_posts = (
        Post.objects.filter(updated_on__gte=time_cutoff)
        .order_by("-aggregate_votes_count")
        .exclude(id__in=ignore_post_ids)[:30]
    )

    users_ids = set()
    posts = []
    for post in all_posts:
        if post.profile.id in users_ids:
            continue
        posts.append(post)
        users_ids.add(post.profile.id)

        if len(users_ids) == 7:
            break
    return posts


def get_popular_posts_from_following_users_last_week(user_profile):
    time_cutoff = timezone.now() - timedelta(days=cutoff_days)
    all_posts = Post.objects.filter(
        updated_on__gte=time_cutoff,
        profile__in=user_profile.following.all(),
        aggregate_votes_count__gte=10,
    ).order_by("-aggregate_votes_count")[:7]
    return list(all_posts)


def get_job_postings():
    time_cutoff = timezone.now() - timedelta(days=cutoff_days)
    jobs = Job.objects.filter(posted_on__gte=time_cutoff, source__in=[Job.JOB_FORM_PAID, Job.GREENHOUSE]).order_by(
        "-posted_on"
    )[:100]

    companies_added = set()
    featured_jobs = []
    for job in jobs:
        if (
            job.company_name in companies_added
            or job.github_username in companies_added
        ):
            continue
        featured_jobs.append(job)
        companies_added.add(job.company_name)
        companies_added.add(job.github_username)
        if len(featured_jobs) == 5:
            break
    return featured_jobs


def get_weekly_digest_posts(user_profile):
    following_posts = get_popular_posts_from_following_users_last_week(user_profile)
    following_post_ids = [post.id for post in following_posts]

    popular_posts = get_global_popular_posts_from_last_week(following_post_ids)

    job_postings = get_job_postings()

    return popular_posts, following_posts, job_postings
