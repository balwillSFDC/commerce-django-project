from datetime import datetime
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib import messages
from django.db import IntegrityError
from django.forms import ModelForm, TextInput, Select, Textarea, URLInput, NumberInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import User, AuctionListing, Bid, Comment


class CreateListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'category', 'image']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'starting_bid': NumberInput(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'image': URLInput(attrs={'class': 'form-control'})
        }


class PlaceBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': NumberInput(attrs={'class': 'form-control'})
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.filter(isActive=True).annotate(highest_bid=Max('bid__amount'))
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@decorators.login_required
def new_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            try:
                new_listing = form.save(commit=False)
                new_listing.owner = request.user
                new_listing.save()

            except:
                messages.error(request, 'There was an issue saving your listing. Please try again.')
                return render(request, "auctions/newlisting.html", {
                    "form": form
                })

            messages.success(request, f"Your listing '{form.cleaned_data['title']}' was saved successfully")
            return HttpResponseRedirect(reverse('new_listing'))

        else:

            return render(request, "auctions/newlisting.html", {
                "form": form
            })

    else:
        return render(request, "auctions/newlisting.html", {
            "form": CreateListingForm()
        })


def listing(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    comments = Comment.objects.filter(listing=listing)

    if request.method == "POST":

        # If user submits bid, evaluate if bid is higher than current bid
        bid_form = PlaceBidForm(request.POST)
        if bid_form.is_valid():
            bid = bid_form.save(commit=False)
            bid.owner = request.user
            bid.listing = listing
   
            # get all bids and check that the bid placed is higher than those currently existing
            if bids.count() > 0:
                if bid.amount > bids[0].amount:
                    bid.save()
                    messages.success(request, "You've successfully submitted your bid for this item!")
                else:
                    messages.error(request, "Your bid must be higher than the highest bid amount")
            else:
                if bid.amount > listing.starting_bid:
                    bid.save()
                    messages.success(request, "You've successfully submitted your bid for this item!")
                else: 
                    messages.error(request, "Your bid must be higher than the starting bid amount")

        # If user submits comment, add to db
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.owner = request.user
            comment.listing = listing
            comment.save()

        # If user clicks 'Add to watchlist' add person to list of people watching
        if request.POST.get('add_to_watchlist', None) == "True":
            listing.people_watching.add(request.user)
        elif request.POST.get('add_to_watchlist', None) == "False":
            listing.people_watching.remove(request.user)
        else:
            pass

        # If owner closes auction, assign the listing to the highest bidder
        if request.POST.get('close_auction', None) == 'True':
            listing.isActive = False
            # If there are bids, assign a winner
            if bids.count() > 0:
                listing.winner = bids[0].owner

            listing.closed_date = datetime.now()
            listing.save()

        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "placebid_form": PlaceBidForm(),
            "bids": bids,
            "highest_bid": bids[0] if bids else None,
            "comments": comments,
            "comment_form": CommentForm()
        })


def watchlist(request):
    watchlist = AuctionListing.objects.filter(people_watching=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": AuctionListing.category.field.choices
    })


def category_items(request, category):
    category_items = AuctionListing.objects.filter(category=category, isActive=True)
    return render(request, "auctions/category_items.html", {
        "category_items": category_items
    })
