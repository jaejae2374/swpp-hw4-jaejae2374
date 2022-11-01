from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=True)
    content = models.TextField(max_length=1000, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
