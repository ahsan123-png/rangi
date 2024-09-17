from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/', include("customer.urls")),
    path('service_provider/', include("serviceProvider.urls")),
    path('', include("userEx.urls")),
]
