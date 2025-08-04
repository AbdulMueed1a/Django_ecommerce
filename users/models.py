from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)

class Seller(models.Model):
    seller_id=models.AutoField(primary_key=True,unique=True)
    seller_user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    seller_store_name=models.CharField()
    # seller_rating=models.FloatField()
    seller_since=models.DateField(auto_now_add=True)
