from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registerCustomer , name='customer')

]
