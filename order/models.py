from django.db import models
from django.conf import settings
from product_view.models import Product

class Order(models.Model):
    Status_Choices=[
        ('completed','Completed'),
        ('canceled','Canceled'),
        ('pending','Pending'),
    ]
    order_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='orders')
    order_date=models.DateField(auto_now_add=True)
    order_status=models.CharField(max_length=30,choices=Status_Choices,default='pending')

class Cart(models.Model):
    cart_id=models.AutoField(primary_key=True)
    cart_buyer=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    cart_subtotal=models.FloatField()

class ProductOrders(models.Model):
    order_id=models.AutoField(primary_key=True)
    order_product=models.ForeignKey(Product,on_delete=models.DO_NOTHING,related_name='items')
    order_quantity=models.IntegerField()
    order_cart=models.ForeignKey(Order,on_delete=models.DO_NOTHING,related_name="cart_products")

class Shipping(models.Model):
    SHIPPING_STATUS=[
        ('staged','Staged'),
        ('packing','Packing'),
        ('dispatched','Dispatched'),
        ('shipped','Shipped'),
        ('arrived','Arrived'),
        ('ofd','Out For Delivery'),
        ('received','Received'),
    ]
    shipping_status=models.CharField(choices=SHIPPING_STATUS,default='staged')
    order_shipment=models.OneToOneField(Order,on_delete=models.CASCADE,related_name='shipment')