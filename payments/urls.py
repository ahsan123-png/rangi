from django.urls import path , include
from.views import *
urlpatterns=[
    path('add_subscription/', add_subscription_plan,name="add_subscription_plan"),
]