from django.db import models
from django.contrib import admin

# Create your models here.
class Blog(models.Model):
    name = models.CharField(max_length=100)
    feed_url = models.CharField(max_length=200)
    github_id = models.CharField(max_length=200)

class Post(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    content = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)
