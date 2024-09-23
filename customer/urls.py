from django.urls import path
from .views import *
urlpatterns = [
    path('register/', registerCustomer, name='customer'),
    path('get/all/', getAllCustomers, name='get_all_customers'),
    path('get/<int:customer_id>/', getCustomer, name='get_customer'),
    path('update/<int:customer_id>/', updateCustomer, name='update_customer'),
    path('delete/<int:customer_id>/', deleteCustomer, name='delete_customer'),
    path('add/reviews/', addReview, name='addReview'),
]