from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from djangoProject import settings

class CustomUser(AbstractUser):
    blocked_users = models.ManyToManyField('self',related_name='blocked_by',null=True,blank=True)



class Blog(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

class BlogFile(models.Model):
    file = models.FileField()
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.CharField(max_length=500)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField()
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)
