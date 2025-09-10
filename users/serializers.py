from rest_framework import serializers
from .models import Seller
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()
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
        model=User
        fields=['email','address','username','first_name','last_name','password','terms_accepted','password_confirm','is_2fa_enabled']

    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already linked to an account')
        return value

    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
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
        password=validated_data.pop('password')

        user=User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class SellerSerializer(serializers.ModelSerializer):
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    rating= serializers.SerializerMethodField()
    class Meta:
        model=Seller
        fields=['user','store_name','rating']


    def get_rating(self,obj):
        from django.db.models import Avg
        result = obj.products.aggregate(average_rating=Avg('p_rating'))
        avg=result['average_rating']
        if avg is None:
            return 0.0
        return avg

    # def create(self, validated_data):
    #     user=self.context['request'].user
    #     return Seller.objects.create(user=user,**validated_data)