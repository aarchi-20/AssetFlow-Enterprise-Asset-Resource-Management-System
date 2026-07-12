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

    if request.method == "POST":
 
        if "add_department" in request.POST:
            name = request.POST.get("dept_name")
            Department.objects.create(name=name)
            messages.success(request, "Department added")
 
        elif "add_category" in request.POST:
            name = request.POST.get("cat_name")
            Category.objects.create(name=name)
            messages.success(request, "Category added")
 
        elif "promote_employee" in request.POST:
            emp_id = request.POST.get("emp_id")
            new_role = request.POST.get("new_role")
            emp = User.objects.filter(id=emp_id).first()
            if emp:
                emp.role = new_role
                emp.save()
                messages.success(request, "Role updated")
 
        return redirect("/organization")
 
    # GET request -> just show everything
    departments = Department.objects.all()
    categories = Category.objects.all()
    employees = User.objects.all()
 
    context = {
        'user': user,
        'departments': departments,
        'categories': categories,
        'employees': employees,
    }
    return render(request, 'organization-setup.html', context)

def assets(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    if request.method == "POST":

        if "register_asset" in request.POST:
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            department_id = request.POST.get("department")
            serial_number = request.POST.get("serial_number")
            acquisition_date = request.POST.get("acquisition_date")
            acquisition_cost = request.POST.get("acquisition_cost")
            condition = request.POST.get("condition")
            location = request.POST.get("location")
 
            category = Category.objects.filter(id=category_id).first()
            department = Department.objects.filter(id=department_id).first()
 
            if acquisition_date == "":
                acquisition_date = None
            if acquisition_cost == "":
                acquisition_cost = None
 
            Asset.objects.create(
                name=name,
                category=category,
                department=department,
                serial_number=serial_number,
                acquisition_date=acquisition_date,
                acquisition_cost=acquisition_cost,
                condition=condition,
                location=location,
            )
            messages.success(request, "Asset registered")
 
        return redirect("/assets")
 
    asset_list = Asset.objects.all()
 
    # basic search/filter - only runs if the person actually used the search box
    search_query = request.GET.get("q")
    if search_query:
        asset_list = asset_list.filter(name__icontains=search_query)
 
    status_filter = request.GET.get("status")
    if status_filter:
        asset_list = asset_list.filter(status=status_filter)
 
    department_filter = request.GET.get("department")
    if department_filter:
        asset_list = asset_list.filter(department_id=department_filter)
 
    categories = Category.objects.all()
    departments = Department.objects.all()
 
    context = {
        'user': user,
        'asset_list': asset_list,
        'categories': categories,
        'departments': departments,
    }
    return render(request, 'assets.html', context)


def allocation(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    if request.method == "POST":
        asset_id = request.POST.get("asset_id")
        asset = Asset.objects.filter(id=asset_id).first()
 
        if "allocate" in request.POST:
            employee_id = request.POST.get("employee_id")
            employee = User.objects.filter(id=employee_id).first()
 
            if asset.status == "ALLOCATED":
                # THE CONFLICT RULE: block it, don't overwrite the current holder
                messages.error(request, f"{asset.tag} is already held by {asset.held_by}. Use Transfer instead.")
            else:
                asset.status = "ALLOCATED"
                asset.held_by = employee
                asset.save()
                AllocationRecord.objects.create(asset=asset, action="ALLOCATED", employee=employee)
                messages.success(request, "Asset allocated")
 
        elif "return_asset" in request.POST:
            notes = request.POST.get("notes")
            AllocationRecord.objects.create(asset=asset, action="RETURNED", employee=asset.held_by, notes=notes)
            asset.status = "AVAILABLE"
            asset.held_by = None
            asset.save()
            messages.success(request, "Asset marked as returned")
 
        elif "transfer" in request.POST:
            new_employee_id = request.POST.get("employee_id")
            new_employee = User.objects.filter(id=new_employee_id).first()
            asset.held_by = new_employee
            asset.save()
            AllocationRecord.objects.create(asset=asset, action="TRANSFERRED", employee=new_employee)
            messages.success(request, "Asset transferred")
 
        return redirect("/allocation")
 
    asset_list = Asset.objects.all()
    employees = User.objects.all()
 
    context = {
        'user': user,
        'asset_list': asset_list,
        'employees': employees,
    }
    return render(request, 'allocation.html', context)

def booking(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    if request.method == "POST":
        asset_id = request.POST.get("asset_id")
        asset = Asset.objects.filter(id=asset_id).first()
        purpose = request.POST.get("purpose")
        start_time = request.POST.get("start_time")   # comes from an <input type="datetime-local">
        end_time = request.POST.get("end_time")
 
        # OVERLAP CHECK - kept simple on purpose:
        # loop through this asset's existing bookings and compare times directly,
        # instead of using fancy ORM query tricks.
        has_conflict = False
        existing_bookings = Booking.objects.filter(asset=asset, status="UPCOMING")
 
        for b in existing_bookings:
            existing_start = str(b.start_time)
            existing_end = str(b.end_time)
            # two time ranges overlap when one starts before the other ends,
            # AND ends after the other starts
            if start_time < existing_end and end_time > existing_start:
                has_conflict = True
                break
 
        if has_conflict:
            messages.error(request, "That slot overlaps with an existing booking")
        else:
            Booking.objects.create(
                asset=asset,
                booked_by=user,
                purpose=purpose,
                start_time=start_time,
                end_time=end_time,
            )
            messages.success(request, "Booking confirmed")
 
        return redirect("/booking")
 
    bookable_assets = Asset.objects.filter(is_bookable=True)
    all_bookings = Booking.objects.all()
 
    context = {
        'user': user,
        'bookable_assets': bookable_assets,
        'all_bookings': all_bookings,
    }

    return render(request, 'booking.html', context)

def maintenance(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    if request.method == "POST":
 
        if "raise_request" in request.POST:
            asset_id = request.POST.get("asset_id")
            issue = request.POST.get("issue_description")
            priority = request.POST.get("priority")
            asset = Asset.objects.filter(id=asset_id).first()
 
            MaintenanceRequest.objects.create(
                asset=asset,
                raised_by=user,
                issue_description=issue,
                priority=priority,
            )
            messages.success(request, "Maintenance request submitted")
 
        elif "approve_request" in request.POST:
            request_id = request.POST.get("request_id")
            req = MaintenanceRequest.objects.filter(id=request_id).first()
            req.status = "APPROVED"
            req.save()
            req.asset.status = "MAINTENANCE"
            req.asset.save()
            messages.success(request, "Request approved")
 
        elif "resolve_request" in request.POST:
            request_id = request.POST.get("request_id")
            req = MaintenanceRequest.objects.filter(id=request_id).first()
            req.status = "RESOLVED"
            req.save()
            req.asset.status = "AVAILABLE"
            req.asset.save()
            messages.success(request, "Marked as resolved")
 
        return redirect("/maintenance")
 
    maintenance_requests = MaintenanceRequest.objects.all()
    asset_list = Asset.objects.all()
 
    context = {
        'user': user,
        'maintenance_requests': maintenance_requests,
        'asset_list': asset_list,
    }
    return render(request, 'maintenance.html', context)

def audit(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    if request.method == "POST":
 
        if "create_cycle" in request.POST:
            dept_id = request.POST.get("department")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            department = Department.objects.filter(id=dept_id).first()
 
            cycle = AuditCycle.objects.create(department=department, start_date=start_date, end_date=end_date)
 
            # auto-create one checklist row per asset held in that department
            dept_assets = Asset.objects.filter(held_by__department=department)
            for a in dept_assets:
                AuditEntry.objects.create(cycle=cycle, asset=a)
 
            messages.success(request, "Audit cycle created")
 
        elif "mark_verdict" in request.POST:
            entry_id = request.POST.get("entry_id")
            verdict = request.POST.get("verdict")   # "VERIFIED" / "MISSING" / "DAMAGED"
            entry = AuditEntry.objects.filter(id=entry_id).first()
            entry.verdict = verdict
            entry.save()
 
            if verdict == "MISSING":
                entry.asset.status = "LOST"
                entry.asset.save()
 
        elif "close_cycle" in request.POST:
            cycle_id = request.POST.get("cycle_id")
            cycle = AuditCycle.objects.filter(id=cycle_id).first()
            cycle.is_closed = True
            cycle.save()
            messages.success(request, "Audit cycle closed")
 
        return redirect("/audit")
 
    cycles = AuditCycle.objects.all()
    departments = Department.objects.all()
 
    context = {
        'user': user,
        'cycles': cycles,
        'departments': departments,
    }
    return render(request, 'audit.html', context)

def reports(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    categories = Category.objects.all()
    category_data = []
    for cat in categories:
        count = Asset.objects.filter(category=cat).count()
        category_data.append({'name': cat.name, 'count': count})
 
    departments = Department.objects.all()
    department_data = []
    for dept in departments:
        count = Asset.objects.filter(held_by__department=dept).count()
        department_data.append({'name': dept.name, 'count': count})
 
    context = {
        'user': user,
        'category_data': category_data,
        'department_data': department_data,
    }
    return render(request, 'reports.html', context)

def notifications(request):
    userid = request.session.get("userid")
    user = User.objects.filter(id=userid).first()

    notification_list = Notification.objects.filter(recipient=user).order_by('-created_at')
 
    context = {
        'user': user,
        'notification_list': notification_list,
    }
    return render(request, 'notifications.html', context)