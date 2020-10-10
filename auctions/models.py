from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
# from django.core.exceptions import ValidationError

class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORIES = [
        ('0', 'No Category'),
        ('1', 'Arts and Crafts'),
        ('2', 'Books'),
        ('3', 'DVDs and Movies'),
        ('4', 'Electronics'),
        ('5', 'Fashion'),
        ('6', 'Health and Beauty'),
        ('7', 'Home'),
        ('8', 'Music'),
        ('9', "Toys"),
        ('10', "Video Games")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=60, blank=False)
    description = models.CharField(max_length=280, blank=False) # same as a tweet :)
    starting_price = models.DecimalField(decimal_places=2, max_digits=10, blank=False, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=2, choices=CATEGORIES, default='0')
    image_link = models.URLField(blank=True, default="")
    creation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, null=False)

    watchers = models.ManyToManyField('User', blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title}"

    def get_price(self):
        price = self.bids.order_by('-amount').first()
        if price is None:
            price = self.starting_price
        else:
            price = price.amount
        return price

    def get_highest_bidder(self):
        if self.starting_price != self.get_price():
            return self.bids.order_by('-amount').first().user
        else:
            return None

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, validators=[MinValueValidator(0)])
    time_placed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: ${self.amount} on {self.listing.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", null=True)
    text = models.CharField(max_length=280, blank=False)
    time_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.listing.title}"
