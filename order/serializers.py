from rest_framework import serializers
from rest_framework import validators
from .models import Cart,Order,CartItems,OrderItems,Shipping

class OrderSerializer(serializers.ModelSerializer):
    items=serializers.StringRelatedField(many=True)
    class Meta:
        model=Order
        fields=['user','items','order_date','order_status']
        read_only_fields=['user']

class CartSerializer(serializers.ModelSerializer):
    items=serializers.StringRelatedField(many=True)
    class Meta:
        model=Cart
        fields=['created_at','updated_at','items','subtotal']

