from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarMake, CarModel, CarDealer, DealerReview
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf, post_request, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

def signup(request):
    return render(request, 'djangoapp/registration.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        name = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=name, password=password)
        if user is not None:
            login(request, user)
            return redirect('/djangoapp')
        else:
            return render(request,'djangoapp/index.html', context)
    


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('/djangoapp')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST['password']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=firstname, last_name=lastname, password=password)
            login(request,user)
            return redirect("/djangoapp")
        else:
            return render(request, 'djangoapp/registration.html', context)

    return render(request, 'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    
    if request.method == "GET":
        url = "http://127.0.0.1:3000/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        dealer_names = " ".join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context = dict()
        context["dealership_list"] = dealerships

        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        dealer_url = "http://127.0.0.1:3000/dealerships/get?id="+str(dealer_id)
        dealer = get_request(dealer_url)
        url = "http://127.0.0.1:5000/api/get_reviews"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        # Concat all dealer's short name
        dealer_names = " ".join([dealer.name for dealer in reviews])
        # Return a list of dealer short name
        print(reviews)
        return render(
            request,
            "djangoapp/dealer_details.html",
            {"reviews": reviews, "dealer_id": dealer_id, "dealer": dealer[0]},
        )

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.method == "GET":
        cars = CarModel.objects.filter(dealerId=dealer_id)
        dealer_url = "http://127.0.0.1:3000/dealerships/get?id="+str(dealer_id)
        dealer = get_request(dealer_url)
        context = {
            "cars": cars,
            "dealer_id": dealer_id,
            "dealer": dealer[0]
        }
        return render(request, "djangoapp/add_review.html", context)
    if request.method == "POST":
        url = "http://127.0.0.1:5000/api/post_review"
        review = {}
        input_data = request.POST
        review["dealership"] = int(dealer_id)
        review["review"] = input_data["content"]
        review["purchase"] = input_data.get("purchasecheck", False)
        review["purchase_date"] = input_data["purchasedate"]
        car = CarModel.objects.get(pk=input_data["car"])
        if car:
            review["car_make"] = car.carMake.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
        else:
            review["car_make"] = "None"
            review["car_model"] = "None"
            review["car_year"] = "None"
        review["name"] = "name"
        review["id"] = 1
        json_payload = {"review": review}
        post_request(url, json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
