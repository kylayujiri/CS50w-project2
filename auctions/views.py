from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import User, Listing, Bid, Comment

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'image_link', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-control'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_link': forms.URLInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class NewBidForm(ModelForm):

    class Meta:
        model = Bid
        fields = ['amount','listing']
        widgets = {
            'amount': forms.TextInput(attrs={'placeholder': 'Bid', 'class': 'form-control'}),
            'listing': forms.HiddenInput()
        }

    def clean_amount(self):
        bid_amount = self.cleaned_data["amount"]
        price = Listing.objects.get(pk=self.data["listing"]).get_price()
        if bid_amount <= price:
            raise ValidationError(
                'Bid must be higher than the current price.',
                code='Invalid'
            )
        return bid_amount


class CategoryFilter(ModelForm):
    class Meta:
        model = Listing
        fields = ['category',]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class NewCommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text',]
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Your Comment', 'class': 'form-control'})
        }

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True)
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

def categories(request):
    if request.method == "POST":
        form = CategoryFilter(request.POST)

        if form.is_valid():

            temp_category = form.save(commit=False)

            return render(request, "auctions/categories.html", {
                "form": form,
                "listings": Listing.objects.filter(is_active=True, category=temp_category.category)
            })

    return render(request, "auctions/categories.html", {
        "form": CategoryFilter
    })

# @login_required
def create_listing(request):
    if request.method == "POST":

        form = NewListingForm(request.POST)

        if form.is_valid():

            new_listing = form.save(commit=False)
            new_listing.user = request.user
            new_listing.save()
            return HttpResponseRedirect(reverse("listing", args=(new_listing.pk,)))

        else:

            return render(request, "auctions/create-listing.html", {
                "form": form
            })

    return render(request, "auctions/create-listing.html", {
        "form": NewListingForm
    })

def profile(request, username):
    not_found = False
    if request.user.is_authenticated and request.user.username == username:
        # we want the profile of the logged in user; send nothing in context
        is_my_profile = True
        username = request.user
    else:
        is_my_profile = False
        try:
            username = User.objects.get(username=username)
        except User.DoesNotExist:
            not_found = True

    return render(request, "auctions/profile.html", {
        "is_my_profile": is_my_profile,
        "not_found": not_found,
        "username": username,
        "listings": Listing.objects.filter(is_active=True, user=User.objects.get(username=username))
    })

def watchlist(request, username):
    if request.user.is_authenticated and request.user.username == username:
        is_my_profile = True
        username = request.user
    else:
        try:
            is_my_profile = False
            username = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse("profile", args=(username,)))

    return render(request, "auctions/watchlist.html", {
        "is_my_profile": is_my_profile,
        "username": username,
        "watchlist": User.objects.get(username=username).watchlist.filter(is_active=True)
    })

def listing(request, listing_id):
    is_my_listing = False
    try:
        requested_listing = Listing.objects.get(pk=listing_id)
        if request.user.is_authenticated and request.user.username == requested_listing.user.username:
            is_my_listing = True
    except Listing.DoesNotExist:
        requested_listing = None

    is_in_my_watchlist = False
    if request.user.is_authenticated and request.user in Listing.objects.get(pk=listing_id).watchers.all():
        is_in_my_watchlist = True

    if request.method == "POST":

        if 'new-bid' in request.POST:
            form = NewBidForm(request.POST)

            if form.is_valid():

                new_bid = form.save(commit=False)
                new_bid.user = request.user
                new_bid.listing = Listing.objects.get(pk=listing_id)
                new_bid.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

            else:

                return render(request, "auctions/listing.html", {
                    "is_in_my_watchlist": is_in_my_watchlist,
                    "is_my_listing": is_my_listing,
                    "listing": requested_listing,
                    "bid_form": form,
                    "comment_form": NewCommentForm,
                    "comments": Comment.objects.filter(listing=requested_listing)
                })

        elif 'add-watchlist' in request.POST:
            Listing.objects.get(pk=listing_id).watchers.add(request.user)
            return HttpResponseRedirect(reverse("watchlist", args=(request.user.username,)))
        elif 'remove-watchlist' in request.POST:
            Listing.objects.get(pk=listing_id).watchers.remove(request.user)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        elif 'close-listing' in request.POST:
            to_close = Listing.objects.get(pk=listing_id)
            to_close.is_active = False
            to_close.save()
            return HttpResponseRedirect(reverse("profile", args=(request.user.username,)))
        elif 'post-comment' in request.POST:
            form = NewCommentForm(request.POST)

            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.user = request.user
                new_comment.listing = Listing.objects.get(pk=listing_id)
                new_comment.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

            else:

                return render(request, "auctions/listing.html", {
                    "is_in_my_watchlist": is_in_my_watchlist,
                    "is_my_listing": is_my_listing,
                    "listing": requested_listing,
                    "bid_form": NewBidForm,
                    "comment_form": form,
                    "comments": Comment.objects.filter(listing=requested_listing)
                })

    return render(request, "auctions/listing.html", {
        "is_in_my_watchlist": is_in_my_watchlist,
        "is_my_listing": is_my_listing,
        "listing": requested_listing,
        "bid_form": NewBidForm(initial={"listing": listing_id,}),
        "comment_form": NewCommentForm,
        "comments": Comment.objects.filter(listing=requested_listing)
    })
