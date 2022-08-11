from django.contrib import admin
from .models import *

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "starting_bid", "owner")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "listing", "comment", "created_date")

class BidAdmin(admin.ModelAdmin): 
    list_display = ("id", "owner", "listing", "amount")

# Register your models here.
admin.site.register(User)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)

