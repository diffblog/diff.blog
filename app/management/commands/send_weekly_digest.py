from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post
from app.digest import get_posts_for_weekly_digest
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core import mail

class Command(BaseCommand):
    help = 'Send the weekly email comprising of top blog posts'

    def add_arguments(self, parser):
        parser.add_argument('--username', action="store", default=None)
        parser.add_argument('--confirm', action="store_true", default=False)
        parser.add_argument('--test-run', action="store_true", default=False)

    def handle(self, *args, **options):
        username = options["username"]
        if options["username"] is None:
            assert(options["confirm"] or options["test_run"])
            users = UserProfile.objects.filter(is_activated=True)
        else:
            user = UserProfile.objects.get(github_username=username)
            users = [user]

        top_posts = get_posts_for_weekly_digest()

        connection = mail.get_connection()   # Use default email connection

        to_emails = []
        for user in users:
            if user.auth is None or not user.auth.email:
                continue
            to_emails.append(user.auth.email)

        subject = 'Popular engineering blog posts of last week'
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_plain = render_to_string('emails/digest.txt', {"top_posts": top_posts})
        msg_html = render_to_string('emails/compiled/digest.html', {"top_posts": top_posts})

        messages = []
        for to_email in to_emails:
            msg = EmailMultiAlternatives(subject, msg_plain, from_email, [to_email])
            msg.attach_alternative(msg_html, "text/html")
            if options["test_run"]:
                print(to_email)
            else:
                messages.append(msg)

        connection.send_messages(messages)
