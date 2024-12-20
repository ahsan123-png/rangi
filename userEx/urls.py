from django.contrib import admin
from django.urls import path , include
from .views import *
urlpatterns = [
    path('category/',addCategory,name="category"),
    path('sub_category/',addSubcategory,name="addSubcategory"),
    path('categories/all/',getCategories,name="getCategories"),
    path('category/<int:category_id>/',getCategory,name="getCategories"),
    path('category/update/<int:category_id>/',updateCategory,name="updateCategory"),
    path('category/delete/<int:category_id>/',deleteCategory,name="deleteCategory"),
    path('categories/subcategories/<int:category_id>/', getSubcategoriesByCategory, name='get_subcategories_by_category'),
    # Subcategory Urls
    path('subcategories/all/',getSubcategories,name="getSubcategories"),
    path('subcategories/get/<int:category_id>/',getSubCategory,name="getSubCategory"),
    path('subcategories/update/<int:subcategory_id>/',updateSubcategory,name="updateSubcategory"),
    path('subcategories/delete/<int:category_id>/',deleteSubCategory,name="deleteSubCategory"),
    # Contact View
    path('contact_us/',contactView,name="contactView"),
    path('contact_us/all',getAllContacts,name="getAllContacts"),
    path('contact_us/<int:contact_id>/',getContactById,name="getContactById"),
    # activation
    path('activate/<str:uidb64>/<str:token>/', activate_user, name='activate_user'),
    # accept request and reject request of a service
    path('service-request/<int:request_id>/accept/', accept_request, name='accept_request'),
    path('service-request/<int:request_id>/reject/', reject_request, name='reject_request'),
    #get all pro by category id
    path('get_all_pro_by_category/<int:category_id>/',getServiceProvidersByCategory, name='getServiceProvidersByCategory'),
    
]
