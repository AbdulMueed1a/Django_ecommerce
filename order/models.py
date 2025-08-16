from django.db import models
from django.conf import settings
from product_view.models import Product

class Order(models.Model):
    Status_Choices=[
        ('completed','Completed'),
        ('paid','Paid'),
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
    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    def save(self,*args,**kwargs):
        if self.order_status=='canceled':
            self.shipment.delete()
        super().save(*args,**kwargs)


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
    @property
    def product_price(self):
        return self.product.p_price*self.quantity
    class Meta:
        unique_together = ['cart', 'product']

    # def save(self,*args,**kwargs):
    #
    #     if self.objects.filter(
    #         product=self.product,
    #         cart__user=self.cart.user
    #     ).exists():
    #         self.quantity+=1
    #         return
    #     super().save(*args,**kwargs)

class OrderItems(models.Model):
    product=models.ForeignKey(Product,
                              on_delete=models.CASCADE
                              )
    quantity=models.PositiveIntegerField(default=1)
    order=models.ForeignKey(Order,
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            related_name="items")
    price_at_purchase=models.DecimalField(decimal_places=2)

    @property
    def total(self):
        return self.price_at_purchase * self.quantity

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
    def save(self,*args,**kwargs):
        if self.shipping_status=='received':
            self.order.order_status='completed'
        super().save(*args,**kwargs)