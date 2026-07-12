from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from .forms import *

# Create your views here.

def login(request):
    if request.method == "POST":

      if "signup" in request.POST:
        form = SignupForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            User.objects.create(name=name, email=email, password=password)

            return redirect("/dashboard")

      elif "login" in request.POST:
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user_obj = User.objects.filter(email=email).first()

            if user_obj and password == user_obj.password:
                request.session["is_login"] = True
                request.session["userid"] = user_obj.id
                return redirect("/dashboard")

            else:
                messages.error(request, "Invalid email or password")

    return render(request, 'login.html')

def dashboard(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    
    return render(request, 'dashboard.html',{'user':user})

def organization(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'organization-setup.html',{'user':user})

def assets(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'assets.html')

def allocation(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'allocation.html')

def booking(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'booking.html')

def maintenance(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'maintenance.html')

def audit(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'audit.html')

def reports(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'reports.html')

def notifications(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'notifications.html')