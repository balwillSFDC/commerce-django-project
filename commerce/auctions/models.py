from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    categories = [
        ('electronics', 'Electronics'),
        ('collectibles_art', 'Collectibles & Art'),
        ('home_garden', 'Home & Garden'),
        ('clothing_shoes_accessories', 'Clothing, Shoes & Accessories'),
        ('toys_hobbies', 'Toys & Hobbies'),
        ('sporting_goods', 'Sporting Goods'),
        ('books_movies_music', 'Books, Movies & Music'),
        ('health_beauty', 'Health & Beauty'),
        ('business_industrial', 'Business & Industrial'),
        ('jewelry_watches', 'Jewelry & Watches'),
        ('baby_essentials', 'Baby Essentials'),
        ('pet_supplies', 'Pet Supplies'),
        ('others', 'Others')
    ]

    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    image = models.URLField(max_length=255, blank=True)
    title = models.CharField('Auction Title', max_length=100, blank=False)
    description = models.CharField('Description', max_length=500, blank=False)
    starting_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    category = models.CharField(choices=categories, blank=True, max_length=100)
    people_watching = models.ManyToManyField(User, related_name="watchlist_items", blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='winner', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    closed_date = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.id} | {self.title}"


class Bid(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, blank=False)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} for listing id {self.listing.id}"


class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, blank=False)
    comment = models.CharField('Comment', max_length=500, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} | {self.comment}"
