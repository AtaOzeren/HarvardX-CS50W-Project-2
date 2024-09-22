from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName=models.CharField(max_length=100)
    
    def __str__ (self):
        return self.categoryName

class Listing (models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    imageUrl = models.URLField(max_length=5000)
    price =models.FloatField()
    isActiv = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user")
    category = models.ForeignKey (Category, on_delete=models.CASCADE,blank=True,null=True,related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    message = models.TextField()

    def __str__(self):
        return f"{self.author} comment on {self.listing}"