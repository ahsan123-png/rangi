from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
################################ USER Modeles ###############################

# Extend the default Django User model
class UserEx(User):
    isServiceProvider = models.BooleanField(default=False)
    isCustomer = models.BooleanField(default=False)
    address = models.CharField(max_length=255, null=True, blank=True)
    zipCode = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=100)
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.username
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
# Subcategory model (e.g., House Cleaning, Carpet Cleaning, etc.)
class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    def __str__(self):
        return f"{self.name} - {self.category.name}"
# Service Provider model
class ServiceProvider(models.Model):
    user = models.OneToOneField(UserEx, on_delete=models.CASCADE)  # Links to the default Django User model
    company_name = models.CharField(max_length=100, null=True, blank=True)  # Optional
    phone_number = models.CharField(max_length=15)
    category = models.ForeignKey(Category, related_name='service_providers', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='service_providers', on_delete=models.CASCADE)
    PEOPLE_CHOICES = [
        ('1', 'Only Me'),
        ('5', 'Under 5 People'),
        ('25', 'Under 25 People'),
        ('50', 'Above 50 People'),
    ]
    number_of_people = models.CharField(max_length=2, choices=PEOPLE_CHOICES)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    def __str__(self):
        return f"{self.user.username} - {self.company_name or 'Individual'}"
# SP Profiles =================
class SPProfile(models.Model):
    service_provider = models.OneToOneField(ServiceProvider, on_delete=models.CASCADE)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    introduction = models.TextField()
    company_founded_date = models.DateField()
    payment_methods = models.CharField(max_length=200)
    services_included = models.ManyToManyField(Subcategory)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
# Employee model (works under a category and subcategory)
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the default Django User model
    phone_number = models.CharField(max_length=15)
    category = models.ForeignKey(Category, related_name='employees', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='employees', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.subcategory.name}"
# Customer model (the person who hires service providers)
class Customer(models.Model):
    user = models.OneToOneField(UserEx, on_delete=models.CASCADE)  # Links to the default Django User model
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='customerDp/', null=True, blank=True)

    def __str__(self):
        return self.user.username
# Reviews model
class Review(models.Model):
    customer = models.ForeignKey(Customer, related_name='reviews', on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()  # Rating out of 5
    comment = models.TextField(null=True, blank=True)  # Optional review comment
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically sets when review is created
    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service_provider.user.username}"
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_images/')  # Upload images to 'review_images/' folder
    def __str__(self):
        return f"Image for Review {self.review.id}"
#============== Contact US ===============
class ContactUs(models.Model):
    """
    Model to store contact us data
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.subject}"
# ============= Service Requests =============
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
]
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategories = models.ManyToManyField(Subcategory)  # Extra services selected by customer
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    request_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
# ============== Service Subscriptions ===============
class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('service_provider', 'Service Provider'),
    ]
    PLAN_TIER_CHOICES = [
        ('basic', 'Basic'),
        ('normal', 'Normal'),
        ('premium', 'Premium'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)  # 'Customer' or 'Service Provider'
    duration = models.CharField(max_length=10, default="monthly")    # Monthly or yearly
    tier = models.CharField(max_length=10, choices=PLAN_TIER_CHOICES)       # Basic, Normal, Premium
    def __str__(self):
        return f"{self.name} - {self.tier} ({self.plan_type})"
# Subscription model to link UserEx and SubscriptionPlan
class UserSubscription(models.Model):
    user = models.ForeignKey(UserEx, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    # Automatically set end_date based on plan duration
    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.plan.duration == 'monthly':
                self.end_date = timezone.now() + timedelta(days=30)
            elif self.plan.duration == 'yearly':
                self.end_date = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)
#============= Payments Details ===================
class Payment(models.Model):
    user = models.ForeignKey(UserEx, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255)  # Stripe's payment intent ID
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment by {self.user.username} of {self.amount}"
