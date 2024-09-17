from django.contrib import admin
from django.urls import path , include
from .views import *
urlpatterns = [
    path('category/',addCategory,name="category"),
    path('sub_category/',addSubcategory,name="addSubcategory"),

]
