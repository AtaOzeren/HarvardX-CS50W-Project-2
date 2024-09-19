from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName=models.CharField(max_length=100)

class Listing (models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    imageUrl = models.URLField(max_length=5000)
    price =models.FloatField()
    isActiv = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user")
    category = models.ForeignKey (Category, on_delete=models.CASCADE,blank=True,null=True,related_name="category")