from rest_framework import serializers
from rest_framework import validators
from .models import Cart,Order,CartItems,OrderItems,Shipping

class OrderSerializer(serializers.ModelSerializer):
    items=serializers.StringRelatedField(many=True)
    class Meta:
        model=Order
        fields=['items','order_date','order_status']
        read_only_fields=['user']

class CartSerializer(serializers.ModelSerializer):
    items=serializers.StringRelatedField(many=True)
    class Meta:
        model=Cart
        fields=['created_at','updated_at','items','subtotal']
        read_only_fields=['user']


class CartItemsSerializers(serializers.ModelSerializer):
    class Meta:
        model=CartItems
        fields=['product',"quantity",'product_price']

    def validate_quantity(self,value):
        if value<0:
            return serializers.ValidationError("Product quantity can't be in negative")


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields=['product','quantity','price_at_purchase','product_price']

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Shipping
        fields=['shipping_status','tracking_id']
