from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Category, Listing, Comment, Bid

def listing(request, id):
    listingData = Listing.objects.get(pk=id)   
    isListingWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request,id):
    listingData = Listing.objects.get(pk=id)
    # DIkkat et 
    listingData.isActive = True 
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    allComments = Comment.objects.filter(listing=listingData)
    isListingWatchlist = request.user in listingData.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "message": "Your auction is closed",
        "update": True,
    })


def addBid(request, id):
    newBid = request.POST["newBid"]
    listingData = Listing.objects.get(pk=id)
    isListingWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if int (newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingData.price.bid = newBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid Successful",
            "update": True,
            "isListingInWatchList": isListingWatchlist,
            "allComments": allComments,  
            "isOwner": isOwner,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid Failed",
            "update": False,
            "isListingInWatchList": isListingWatchlist,
            "allComments": allComments, 
            "isOwner": isOwner, 
        })

def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newComment']
    
    newComment = Comment(
        author = currentUser,
        listing = listingData, 
        message = message,
    )
    newComment.save() 
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, ))) 
    
def index(request):
    activeListings = Listing.objects.filter(isActiv=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": allCategories,
    })

def displayCategory (request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        category = Category.objects.get(categoryName= categoryFromForm)
        activeListings = Listing.objects.filter(isActiv=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activeListings,
            "categories": allCategories,
    })

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        title = request.POST.get("title")
        description = request.POST.get("description")
        imageUrl = request.POST.get("imageurl")
        price = float(request.POST.get("price")) 
        category = request.POST.get("category")

        currentUser = request.user

        bid=Bid(bid=float(price),user=currentUser)
        bid.save()
        # Creating a new ad and catching errors
        try:
            categoryData = Category.objects.get(categoryName=category)
        except Category.DoesNotExist:
            return render(request, "auctions/create.html", {
                "message": "Selected category does not exist.",
                "categories": Category.objects.all()
            })

        # Creating a new ad and catching errors
        try:
            newListing = Listing(
                title=title,
                description=description,
                imageUrl=imageUrl,
                price=bid,
                owner=currentUser,
                category=categoryData,
            )
            newListing.save()
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            return render(request, "auctions/create.html", {
                "message": f"Error saving listing: {e}",
                "categories": Category.objects.all()
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
