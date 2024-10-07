from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registerServiceProvider, name='register_service_provider'),
    path('login/', loginView, name='loginView'),
    path('get/all/', getAllServiceProviders, name='getAllServiceProviders'),
    path('status/<int:id>/', updateServiceProviderStatus, name='updateServiceProviderStatus'),
    path('update/user/<int:provider_id>/', updateServiceProvider, name='updateServiceProvider'),
    path('get/<int:provider_id>/', getServiceProvider, name='getServiceProvider'),
    path('delete/<int:provider_id>/', deleteServiceProvider, name='deleteServiceProvider'),
    path('search/', listServiceProviders, name='listServiceProviders'),
    path('create/profile/<int:service_provider_id>/', createSpProfile, name='createSpProfile'),
    path('create/service/request/', createServiceRequest, name='createServiceRequest'),
    path('update/profile/<int:service_provider_id>/', updateSpProfile, name='update_sp_profile'),
    path('update/profile/image/<int:service_provider_id>/', updateSpProfilePicture, name='updateSpProfilePicture'),
]
