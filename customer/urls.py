from django.urls import path
from .views import *
urlpatterns = [
    path('register/', registerCustomer, name='customer'),
    path('get/all/', getAllCustomers, name='get_all_customers'),
    path('get/<int:customer_id>/', getCustomer, name='get_customer'),
    path('update/<int:customer_id>/', updateCustomer, name='update_customer'),
    path('delete/<int:customer_id>/', deleteCustomer, name='delete_customer'),
    path('add/reviews/', addReview, name='addReview'),
    path('reviews/serviceprovider/<int:service_provider_id>/',getReviewsByServiceProvider, name='get_reviews_by_service_provider'),
    path('review/update/<int:review_id>/', updateReview, name='update_review'),  # 
    path('review/delete/<int:review_id>/', deleteReview, name='delete_review'), 
]