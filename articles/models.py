from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Articles(models.Model):
    title = models.TextField(max_length= 256)
    body = models.TextField(max_length= 500)
    likes = models.IntegerField(default= 0)

class Comments(models.Model):
    article = models.ForeignKey(Articles)
    text = models.TextField(max_length= 500)