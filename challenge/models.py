from django.db import models

# Create your models here.
class Count(models.Model):
    BOOKS = 1
    type = models.IntegerField(default=0)
    value = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)


class LastId(models.Model):
    type = models.IntegerField(default=0)
    response_id = models.CharField(max_length=100)
