from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registerServiceProvider, name='register_service_provider'),
    path('get/all/', getAllServiceProviders, name='getAllServiceProviders'),
    path('update/user/<int:provider_id>/', updateServiceProvider, name='updateServiceProvider'),
    path('get/<int:provider_id>/', getServiceProvider, name='getServiceProvider'),
    path('delete/<int:provider_id>/', deleteServiceProvider, name='deleteServiceProvider'),
]
