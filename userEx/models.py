from django.db import models
from django.contrib.auth.models import User
################################ USER Modeles ###############################

# Extend the default Django User model
class UserEx(User):
    isServiceProvider = models.BooleanField(default=False)  # True for service providers, False for others
    isCustomer = models.BooleanField(default=False)  # True for customers, False for others
    address = models.CharField(max_length=255, null=True, blank=True)  # Optional address field
    zipCode = models.CharField(max_length=10, null=True, blank=True)  # Optional zip code field
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Subcategory model (e.g., House Cleaning, Carpet Cleaning, etc.)
class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

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