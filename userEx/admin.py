from django.contrib import admin
from .models import *
# Register your models here.
models = [UserEx,ServiceProvider, Category, Subcategory,SubscriptionPlan,UserSubscription,Payment]

for model in models:
    admin.site.register(model)