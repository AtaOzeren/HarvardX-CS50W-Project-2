from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import User, Category, Listing, Comment, Bid

def listing(request, id):
    listing_data = get_object_or_404(Listing, pk=id)
    is_listing_watchlist = request.user in listing_data.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    is_owner = request.user == listing_data.owner

    context = {
        "listing": listing_data,
        "isListingInWatchList": is_listing_watchlist,
        "allComments": all_comments,
        "isOwner": is_owner
    }
    return render(request, "auctions/listing.html", context)

def close_auction(request, id):
    listing_data = get_object_or_404(Listing, pk=id)

    if request.user != listing_data.owner:
        return HttpResponseRedirect(reverse("listing", args=[id]))

    listing_data.isActive = False  # Açık artırma kapatıldı
    listing_data.save()

    context = {
        "listing": listing_data,
        "isListingInWatchList": request.user in listing_data.watchlist.all(),
        "allComments": Comment.objects.filter(listing=listing_data),
        "isOwner": True,
        "message": "Your auction is closed",
        "update": True
    }
    return render(request, "auctions/listing.html", context)

def add_bid(request, id):
    listing_data = get_object_or_404(Listing, pk=id)
    new_bid = int(request.POST.get("newBid", 0))

    if new_bid <= listing_data.price.bid:
        message = "Bid Failed"
        update = False
    else:
        Bid.objects.create(user=request.user, bid=new_bid)
        listing_data.price.bid = new_bid
        listing_data.save()
        message = "Bid Successful"
        update = True

    context = {
        "listing": listing_data,
        "message": message,
        "update": update,
        "isListingInWatchList": request.user in listing_data.watchlist.all(),
        "allComments": Comment.objects.filter(listing=listing_data),
        "isOwner": request.user == listing_data.owner,
    }
    return render(request, "auctions/listing.html", context)

def add_comment(request, id):
    listing_data = get_object_or_404(Listing, pk=id)
    message = request.POST.get("newComment", "")

    if message:
        Comment.objects.create(author=request.user, listing=listing_data, message=message)

    return HttpResponseRedirect(reverse("listing", args=[id]))

def display_watchlist(request):
    current_user = request.user
    listings = current_user.listingWatchlist.all()

    return render(request, "auctions/watchlist.html", {"listings": listings})

def add_watchlist(request, id):
    listing_data = get_object_or_404(Listing, pk=id)
    current_user = request.user

    listing_data.watchlist.add(current_user)
    return HttpResponseRedirect(reverse("listing", args=[id]))

def remove_watchlist(request, id):
    listing_data = get_object_or_404(Listing, pk=id)
    current_user = request.user

    listing_data.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing", args=[id]))

def index(request):
    active_listings = Listing.objects.filter(isActive=True)
    categories = Category.objects.all()

    context = {
        "listings": active_listings,
        "categories": categories,
    }
    return render(request, "auctions/index.html", context)

def display_category(request):
    if request.method == "POST":
        category_name = request.POST.get("category", "")
        category = get_object_or_404(Category, categoryName=category_name)
        active_listings = Listing.objects.filter(isActive=True, category=category)
        categories = Category.objects.all()

        context = {
            "listings": active_listings,
            "categories": categories
        }
        return render(request, "auctions/index.html", context)

def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": categories})

    title = request.POST.get("title", "")
    description = request.POST.get("description", "")
    image_url = request.POST.get("imageurl", "")
    price = float(request.POST.get("price", 0))
    category_name = request.POST.get("category", "")

    current_user = request.user
    bid = Bid.objects.create(bid=price, user=current_user)

    try:
        category_data = Category.objects.get(categoryName=category_name)
        new_listing = Listing.objects.create(
            title=title,
            description=description,
            imageUrl=image_url,
            price=bid,
            owner=current_user,
            category=category_data,
        )
        return HttpResponseRedirect(reverse("index"))
    except Category.DoesNotExist:
        return render(request, "auctions/create.html", {
            "message": "Selected category does not exist.",
            "categories": Category.objects.all()
        })
    except Exception as e:
        return render(request, "auctions/create.html", {
            "message": f"Error saving listing: {e}",
            "categories": Category.objects.all()
        })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})

    return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation", "")

        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})

    return render(request, "auctions/register.html")
