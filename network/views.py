from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import request
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import *
from .util import *


#Langing page of the application
def index(request):
    # Get all posts
    all_posts = Post.objects.all()
    
    # Get the current page
    page = request.GET.get('page')
    
    return render(request, "network/index.html", {
        "posts": paginate(all_posts, page), # add pagination to it using paginate function created in util.py
        'page': page #send in page along with it for showing thw current page
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Add post
@csrf_exempt
@login_required
def add_post(request):
    if request.method == "POST": #If request is post request do this
        content = json.loads(request.body) #get the data from post request 
        
        post = Post(content=content, created_by=request.user) # Create a post using Post model
        post.save() # Save the post

        return JsonResponse({"message": "Post successfully added"}) # send a success message


# Like post
@csrf_exempt
@login_required
def like_post(request):
    if request.method == "PUT": # if method is put do this, that is like the post
        res = json.loads(request.body) #get the data
        post = Post.objects.get(pk = res['post']) # get post details
        user = User.objects.get(pk = request.user.id) # get user details

        post.like.add(user) # Add like to the post from the current user

        return JsonResponse({"count": f"{post.like.count()}"}) # send the post count to update

    if request.method == "DELETE": # if method is delete do this, that is delete the post like
        res = json.loads(request.body) # Get data
        post = Post.objects.get(pk = res['post']) # get post
        user = User.objects.get(pk = request.user.id) # get user to unlike

        post.like.remove(user) #remove like

        return JsonResponse({"count": f"{post.like.count()}"}) #send the like count

def profile(request, user_id): # show profile
    user = User.objects.get(pk = user_id) # get the user profile
    posts = user.post.all() # show all posts
    followers = User.objects.filter(following=user) # get all followers
    
    page = request.GET.get('page') #get the page for pagination

    return render(request, "network/profile.html", {
        "posts": paginate(posts, page), #send the paginated posts
        "page": page, #send the page 
        "user_profile": user, # user profile details
        "followers": followers # send the followers of user
    })

# editing post
@csrf_exempt
@login_required
def edit_post(request, post_id):
    if request.method == "PUT": #put to update
        post = Post.objects.get(pk = post_id)
        res = json.loads(request.body)

        if post.created_by == request.user: #only if created_by and current user are same allow this
            post.content = res["content"]  # edit content
            post.save() #save
            
            return JsonResponse({"content": f"{post.content}"}) #send the updated content

        else:
            return JsonResponse({"error": "You cannot edit other users post"}) #if created_by and request.user are not same do not allow

@login_required
def following(request): # following page
    user = User.objects.get(pk = request.user.id) # get current user
    following = user.following.all() # get all who current user follows

    following_posts = Post.objects.filter(created_by__in=following) # get all the follwong posts
    #created_by__in: double underscore mean that check in the list of created_by and filter

    page = request.GET.get('page')

    return render(request, "network/following.html", {
        "posts": paginate(following_posts, page),
        "page": page
    })


@csrf_exempt
@login_required
def follow(request): # follow or unfollow
    user = User.objects.get(pk = request.user.id)
    
    if request.method == "POST": # post create follow
        res = json.loads(request.body)
        user_to_follow = User.objects.get(pk = res['user']) # get data of user to follow

        if user_to_follow == user: #if user_to_follow and current user are same show error
            return JsonResponse({"error": "You cannot follow yourself"})

        user.following.add(user_to_follow) # if it is not same add

        return JsonResponse({"followers_count": f"{User.objects.filter(following=user_to_follow).count()}"}) #send the followers count
    
    if request.method == "DELETE": # delete the user following
        res = json.loads(request.body)

        user_to_unfollow = User.objects.get(pk = res['user'])

        user.following.remove(user_to_unfollow) #removed

        return JsonResponse({"followers_count": f"{User.objects.filter(following=user_to_unfollow).count()}"}) # send follower count
        