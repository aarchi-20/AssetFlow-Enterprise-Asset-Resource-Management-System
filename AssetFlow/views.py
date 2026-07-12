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

def logout(request):
    request.session.flush()   # clears the whole session -> logs the user out
    return redirect("/")


def dashboard(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    available_count = Asset.objects.filter(status="AVAILABLE").count()
    allocated_count = Asset.objects.filter(status="ALLOCATED").count()
    maintenance_count = Asset.objects.filter(status="MAINTENANCE").count()
    booking_count = Booking.objects.filter(status="UPCOMING").count()
 
    context = {
        'user': user,
        'available_count': available_count,
        'allocated_count': allocated_count,
        'maintenance_count': maintenance_count,
        'booking_count': booking_count,
    }
    return render(request, 'dashboard.html', context)

def organization(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'organization-setup.html',{'user':user})

def assets(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'assets.html',{'user':user})

def allocation(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'allocation.html',{'user':user})

def booking(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'booking.html',{'user':user})

def maintenance(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'maintenance.html',{'user':user})

def audit(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'audit.html',{'user':user})

def reports(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'reports.html',{'user':user})

def notifications(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()
    return render(request, 'notifications.html',{'user':user})