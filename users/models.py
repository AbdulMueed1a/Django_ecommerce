import uuid
from datetime import timedelta
from pyotp import random_base32
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import validate_email
from django.utils import timezone


class CustomUser(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    email= models.EmailField(unique=True,validators=[validate_email])
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_2fa_enabled = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    @property
    def is_seller(self):
        return Seller.objects.filter(user=self).exists()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def save(self,*args,**kwargs):
        if self.is_2fa_enabled and not self.otp_secret:
            self.otp_secret=random_base32()
        super().save(*args,**kwargs)

class Seller(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    store_name=models.CharField(unique=True)
    is_active=models.BooleanField(default=True)
    since=models.DateField(auto_now_add=True)


class EmailToken(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    token=models.UUIDField(default=uuid.uuid4,unique=True)
    used=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField()
    def save(self,*args,**kwargs):
        if not self.expires_at:
            self.expires_at=timezone.now()+timedelta(hours=24)
        super().save(*args,**kwargs)
    @property
    def is_expired(self):
        return timezone.now()>self.expires_at