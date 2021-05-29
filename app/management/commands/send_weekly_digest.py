import time

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post
from app.digest import get_weekly_digest_posts
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core import mail
from django.urls import reverse


class Command(BaseCommand):
    help = "Send the weekly email comprising of top blog posts"

    def add_arguments(self, parser):
        parser.add_argument("--username", action="store", default=None)
        parser.add_argument("--confirm", action="store_true", default=False)
        parser.add_argument("--test-run", action="store_true", default=False)

    def handle(self, *args, **options):
        username = options["username"]
        if options["username"] is None:
            assert options["confirm"] or options["test_run"]
            users = UserProfile.objects.filter(
                is_activated=True, send_weekly_digest_email=True
            )
        else:
            user = UserProfile.objects.get(github_username=username)
            users = [user]

        connection = mail.get_connection()  # Use default email connection

        to_users = []
        for user in users:
            if user.auth is None or not user.auth.email:
                continue
            to_users.append(user)

        subject = "Best engineering blog posts of last week"
        from_email = settings.DEFAULT_FROM_EMAIL

        messages = []
        for to_user in to_users:
            to_email = to_user.auth.email
            unsubscribe_link = "https://diff.blog{}".format(
                reverse(
                    "unsubscribe_from_emails", kwargs={"key": to_user.unsubscribe_key}
                )
            )
            global_posts, following_posts = get_weekly_digest_posts(to_user)
            context = {
                "global_posts": global_posts,
                "following_posts": following_posts,
                "unsubscribe_link": unsubscribe_link,
            }
            msg_plain = render_to_string("emails/digest.txt", context)
            msg_html = render_to_string("emails/compiled/digest.html", context)
            msg = EmailMultiAlternatives(subject, msg_plain, from_email, [to_email])
            msg.attach_alternative(msg_html, "text/html")
            if options["test_run"]:
                print(to_email)
            else:
                messages.append(msg)

        if len(messages) > 1:
            print("Waiting for 5 seconds before sending email")
            time.sleep(5)
        connection.send_messages(messages)
