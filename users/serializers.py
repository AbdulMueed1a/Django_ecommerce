from rest_framework import serializers
from .models import Seller,CustomUser
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type':'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    terms_accepted=serializers.BooleanField(write_only=True)
    class Meta:
        model=CustomUser
        fields=['email','address','username','first_name','last_name','password','terms_accepted','password_confirm','is_2fa_enabled']

    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already linked to an account')
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError('Must accept Terms and Conditions')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('password_confirm',None):
            raise serializers.ValidationError('passwords do not match')
        attrs.pop('terms_accepted',None)
        return attrs


    def create(self, validated_data):
        user=CustomUser.objects.create(password=validated_data.pop('password'),**validated_data)
        return user

class SellerSerializer(serializers.ModelSerializer):
    seller_rating= serializers.SerializerMethodField()
    class Meta:
        model=Seller
        fields=['seller_user','seller_store_name','seller_rating']

    def get_seller_rating(self,obj):
        from django.db.models import Avg
        result = obj.products.aggregate(average_rating=Avg('p_rating'))
        avg=result['average_rating']
        if avg is None:
            return 0.0
        return avg