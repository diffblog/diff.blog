from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from app.models import Topic, UserProfile, UserList, Post
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

import requests

class Command(BaseCommand):
    help = 'Send the weekly email comprising of top blog posts'

    def handle(self, *args, **options):
        time_cutoff = timezone.now() - timedelta(days=7)
        top_posts = Post.objects.filter(updated_on__gte=time_cutoff).order_by("-aggregate_votes_count")[:30]

        subject, from_email, to = 'hello', settings.DEFAULT_FROM_EMAIL, "yo@vishnuks.com"
        text_content = 'This is an important message.'
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
