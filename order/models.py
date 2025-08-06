from django.db import models
from django.conf import settings
from product_view.models import Product

class Order(models.Model):
    Status_Choices=[
        ('completed','Completed'),
        ('canceled','Canceled'),
        ('pending','Pending'),
    ]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='orders')
    order_date=models.DateField(auto_now_add=True)
    order_status=models.CharField(max_length=30,
                                  choices=Status_Choices,
                                  default='pending')

class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def subtotal(self):
        return sum(item.product.p_price for item in self.items.all())

class CartItems(models.Model):
    product=models.ForeignKey(Product,
                              on_delete=models.CASCADE,
                              related_name='cart')
    quantity=models.PositiveIntegerField(default=1)
    cart=models.ForeignKey(Cart,
                           on_delete=models.CASCADE,
                           related_name='items')
    def __str__(self):
        return self.product.p_title

    def save(self,*args,**kwargs):

        if self.objects.filter(
            product=self.product,
            cart__user=self.cart.user
        ).exists():
            self.quantity+=1
            return
        super().save(*args,**kwargs)

class OrderItems(models.Model):
    product=models.ForeignKey(Product,
                              on_delete=models.CASCADE,
                              related_name='items')
    quantity=models.PositiveIntegerField(default=1)
    order=models.ForeignKey(Order,
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            related_name="cart_products")
    price_at_purchase=models.DecimalField()

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
    shipping_address=models.TextField()
    tracking_id=models.CharField(max_length=20)
    shipping_status=models.CharField(
        choices=SHIPPING_STATUS,
        default='staged')
    order=models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='shipment')