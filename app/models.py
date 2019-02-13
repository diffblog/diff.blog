from django.db import models
from django.contrib.auth.models import AbstractUser, User

# Create your models here.
class UserProfile(models.Model):
    extra_data = models.TextField()
    auth = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="profile")
    feed_url = models.CharField(max_length=200)
    github_username = models.CharField(max_length=50)
    github_id = models.IntegerField()
    github_token = models.CharField(max_length=50, null=True)
    is_activated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50)
