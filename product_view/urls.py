from .views import Product
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', Product.as_view(), name='Product_view'),
]