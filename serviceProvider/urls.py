from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registerServiceProvider, name='register_service_provider'),
    path('get/all/', getAllServiceProviders, name='getAllServiceProviders'),
]
