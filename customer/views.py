from django.shortcuts import render
from userEx.models import *
# Create your views here.

def registerCustomer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        isServiceProvider = False
        isCustomer = True
        address = request.POST['address']
        zipCode = request.POST['zipCode']
        name = request.POST['name']