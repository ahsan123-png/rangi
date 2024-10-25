from django.urls import path , include
from.views import *
urlpatterns=[
    path('add_subscription/', addSubscriptionPlan,name="add_subscription_plan"),
]