from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)   
    ROLE_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("DEPT_HEAD", "Department Head"),
        ("ASSET_MANAGER", "Asset Manager"),
        ("ADMIN", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="EMPLOYEE")
    department = models.ForeignKey("Department", null=True, blank=True, on_delete=models.SET_NULL)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent_department = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    head = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="heads")
    is_active = models.BooleanField(default=True)

class Category(models.Model):
    name = models.CharField(max_length=50)

class Asset(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"), ("ALLOCATED", "Allocated"), ("RESERVED", "Reserved"),
        ("MAINTENANCE", "Under Maintenance"), ("LOST", "Lost"), ("RETIRED", "Retired"), ("DISPOSED", "Disposed"),
    ]
    tag = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=100)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=50)
    location = models.CharField(max_length=150)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    is_bookable = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="AVAILABLE")
    held_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="held_assets")
    expected_return_date = models.DateField(null=True)

class AllocationRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=25)   # "ALLOCATED" / "RETURNED" / "TRANSFERRED"
    employee = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
 

class Booking(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=15, default="UPCOMING")
 
 
class MaintenanceRequest(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="maintenance_requests")
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_description = models.TextField()
    priority = models.CharField(max_length=10, default="MEDIUM")
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
 
 
class AuditCycle(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Asset, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
 
 
class AuditEntry(models.Model):
    cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE, related_name="entries")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    verdict = models.CharField(max_length=10, default="PENDING")   # VERIFIED / MISSING / DAMAGED
 
 
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
 