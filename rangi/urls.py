from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/', include("customer.urls")),
    path('service_provider/', include("serviceProvider.urls")),
    path('', include("userEx.urls")),
    path('accounts/', include('allauth.urls')),
    path('payments/', include('payments.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)